"""Latest YouTube videos for a list of channels, via public Atom feeds."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache

CHANNEL_URL = "https://www.youtube.com/{handle}"
FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
# The channel Atom feed mixes Shorts/clips in with regular videos. YouTube
# also publishes a long-form-only feed via the channel's "uploads, long-form"
# (UULF) playlist, which matches what the channel's "Videos" tab shows. The
# playlist ID is derived from the channel ID by swapping the "UC" prefix for
# "UULF".
UULF_FEED_URL = "https://www.youtube.com/feeds/videos.xml?playlist_id=UULF{suffix}"
# Unofficial internal endpoint (used by the YouTube apps themselves). Serves
# caption-track metadata; the WEB client gets no tracks without auth, but the
# ANDROID client does. Most breakage-prone part of this module.
PLAYER_URL = "https://www.youtube.com/youtubei/v1/player"
_PLAYER_CLIENT = {"clientName": "ANDROID", "clientVersion": "20.10.38"}
_CHANNEL_ID_RE = re.compile(r"UC[0-9A-Za-z_-]{22}")
_USER_AGENT = "Mozilla/5.0 (compatible; youtube-latest/0.1)"

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


class ChannelNotFoundError(Exception):
    """A handle could not be resolved to a YouTube channel ID."""


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _post_json(url: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": _USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def _fetch_transcript(video_id: str) -> tuple[str | None, str | None]:
    """Return (transcript_text, language_code) for a video, or (None, None)
    when the video has no captions or the (unofficial) endpoint fails."""
    try:
        data = _post_json(
            PLAYER_URL, {"context": {"client": _PLAYER_CLIENT}, "videoId": video_id}
        )
        tracks = (
            data.get("captions", {})
            .get("playerCaptionsTracklistRenderer", {})
            .get("captionTracks", [])
        )
        if not tracks:
            return None, None
        # kind == "asr" marks auto-generated captions; prefer a manual track.
        track = min(tracks, key=lambda t: t.get("kind") == "asr")
        root = ET.fromstring(_fetch(track["baseUrl"]))
        parts = []
        for p in root.iter("p"):
            text = "".join(p.itertext()).strip()
            if text:
                parts.append(text)
        return (" ".join(parts) or None), track.get("languageCode")
    except Exception:
        return None, None


def _is_channel_id(s: str) -> bool:
    return bool(_CHANNEL_ID_RE.fullmatch(s))


def _normalize(channel: str) -> str:
    if _is_channel_id(channel) or channel.startswith("@"):
        return channel
    return "@" + channel


def resolve_channel_id(handle: str) -> str:
    normalized = _normalize(handle)
    if _is_channel_id(normalized):
        return normalized
    return _resolve_handle(normalized)


@lru_cache(maxsize=None)
def _resolve_handle(h: str) -> str:
    try:
        html = _fetch(CHANNEL_URL.format(handle=h))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ChannelNotFoundError(f"channel not found: {h}") from e
        raise
    # Priority matters: a channel page can embed OTHER channels' IDs (e.g. in
    # related/recommended-channel data) under the "channelId" key before the
    # real channel's ID appears. The canonical link / og:url and the
    # "externalId" key reliably refer to the page's own channel, so they are
    # tried first; the bare "channelId" key is only a last resort.
    m = (
        re.search(r"youtube\.com/channel/(UC[0-9A-Za-z_-]{22})", html)
        or re.search(r'"externalId":"(UC[0-9A-Za-z_-]{22})"', html)
        or re.search(r'"channelId":"(UC[0-9A-Za-z_-]{22})"', html)
    )
    if m is None:
        raise ChannelNotFoundError(f"could not find a channel ID on the page for {h}")
    return m.group(1)


resolve_channel_id.cache_clear = _resolve_handle.cache_clear


def _parse_feed(xml_text: str, n: int) -> dict:
    root = ET.fromstring(xml_text)
    videos = []
    for entry in root.findall("atom:entry", _NS)[:n]:
        video_id = entry.findtext("yt:videoId", default="", namespaces=_NS)
        published = entry.findtext("atom:published", default=None, namespaces=_NS)
        thumbnail = None
        views = None
        description = None
        group = entry.find("media:group", _NS)
        if group is not None:
            thumb = group.find("media:thumbnail", _NS)
            if thumb is not None:
                thumbnail = thumb.get("url")
            stats = group.find("media:community/media:statistics", _NS)
            if stats is not None and stats.get("views") is not None:
                views = int(stats.get("views"))
            description = group.findtext("media:description", default=None, namespaces=_NS)
        videos.append(
            {
                "video_id": video_id,
                "title": entry.findtext("atom:title", default="", namespaces=_NS),
                "description": description,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "published": datetime.fromisoformat(published) if published else None,
                "thumbnail": thumbnail,
                "views": views,
            }
        )
    # Channel feeds have the channel name in the root <title>. Playlist feeds
    # (e.g. the UULF long-form playlist) put "Videos" (the playlist name) in
    # <title> and the actual channel name in <author><name>. Prefer
    # author/name when present so channel_title is correct for both.
    channel_title = root.findtext("atom:author/atom:name", default=None, namespaces=_NS)
    if not channel_title:
        channel_title = root.findtext("atom:title", default="", namespaces=_NS)
    return {
        "channel_title": channel_title,
        "videos": videos,
    }


_MAX_WORKERS = 8


def _channel_result(channel: str, n: int, include_shorts: bool) -> dict:
    norm = _normalize(channel)
    try:
        channel_id = resolve_channel_id(channel)
        feed = None
        if not include_shorts:
            suffix = channel_id[2:]  # strip "UC" prefix for the UULF playlist ID
            try:
                uulf_feed = _parse_feed(_fetch(UULF_FEED_URL.format(suffix=suffix)), n)
                if uulf_feed["videos"]:
                    feed = uulf_feed
            except Exception:
                feed = None
        if feed is None:
            # Fall back to the mixed channel feed (Shorts/clips included) if
            # the long-form-only UULF playlist feed is unavailable or empty,
            # or directly when include_shorts=True was requested.
            feed = _parse_feed(_fetch(FEED_URL.format(channel_id=channel_id)), n)
        return {"channel": norm, "channel_id": channel_id, **feed}
    except Exception as e:
        return {"channel": norm, "error": str(e)}


def latest_videos(
    channels: list[str],
    n: int = 5,
    include_shorts: bool = False,
    include_transcripts: bool = False,
) -> list[dict]:
    """Return a flat list with one dict per video, channels in input order
    and newest-first within each channel. A failed channel contributes
    exactly one element: {"channel_handle": ..., "error": "<msg>"}.

    By default, fetches the long-form-only UULF playlist feed (falling back
    to the mixed channel feed on error or if it's empty). If
    include_shorts=True, fetches the mixed channel feed directly, so Shorts
    and clips appear alongside videos.
    """
    if not channels:
        return []
    n = max(1, min(n, 15))
    workers = min(_MAX_WORKERS, len(channels))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        channel_results = list(
            ex.map(lambda c: _channel_result(c, n, include_shorts), channels)
        )

    flat: list[dict] = []
    for r in channel_results:
        if "error" in r:
            flat.append({"channel_handle": r["channel"], "error": r["error"]})
            continue
        for v in r["videos"]:
            flat.append(
                {
                    "channel_handle": r["channel"],
                    "channel_id": r["channel_id"],
                    "channel_name": r["channel_title"],
                    "video_id": v["video_id"],
                    "title": v["title"],
                    "description": v["description"],
                    "url": v["url"],
                    "published": v["published"],
                    "thumbnail": v["thumbnail"],
                    "views": v["views"],
                }
            )

    if include_transcripts:
        # Two extra HTTP requests per video (player call + caption fetch),
        # hence opt-in. Failures degrade to None rather than erroring the row.
        vids = [r for r in flat if "error" not in r]
        if vids:
            with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(vids))) as ex:
                transcripts = ex.map(lambda r: _fetch_transcript(r["video_id"]), vids)
                for r, (text, lang) in zip(vids, transcripts):
                    r["transcript"] = text
                    r["transcript_language"] = lang
    return flat


def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"not JSON serializable: {type(obj)!r}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Show the latest videos for YouTube channels."
    )
    parser.add_argument("channels", nargs="+", help="channel handles (@name) or UC... IDs")
    parser.add_argument("-n", type=int, default=5, help="videos per channel (max 15)")
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    parser.add_argument(
        "--transcripts",
        action="store_true",
        dest="include_transcripts",
        help="also fetch each video's transcript (2 extra requests per video)",
    )
    parser.add_argument(
        "--include-shorts",
        action="store_true",
        dest="include_shorts",
        help="include Shorts/clips (mixed feed) instead of long-form only",
    )
    args = parser.parse_args(argv)

    results = latest_videos(
        args.channels,
        n=args.n,
        include_shorts=args.include_shorts,
        include_transcripts=args.include_transcripts,
    )

    if args.as_json:
        print(json.dumps(results, default=_json_default, indent=2))
    else:
        current_channel = None
        for r in results:
            if "error" in r:
                if current_channel is not None:
                    print()
                    current_channel = None
                print(f"{r['channel_handle']}: error: {r['error']}")
                continue
            if r["channel_handle"] != current_channel:
                if current_channel is not None:
                    print()
                print(f"{r['channel_name']} ({r['channel_handle']})")
                current_channel = r["channel_handle"]
            date = r["published"].date().isoformat() if r["published"] else "?"
            views = f"{r['views']:,} views" if r["views"] is not None else "views n/a"
            print(f"  [{date}] {r['title']} — {views}")
            print(f"          {r['url']}")

    return 1 if any("error" in r for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
