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
    m = re.search(r'"channelId":"(UC[0-9A-Za-z_-]{22})"', html) or re.search(
        r"youtube\.com/channel/(UC[0-9A-Za-z_-]{22})", html
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
        group = entry.find("media:group", _NS)
        if group is not None:
            thumb = group.find("media:thumbnail", _NS)
            if thumb is not None:
                thumbnail = thumb.get("url")
            stats = group.find("media:community/media:statistics", _NS)
            if stats is not None and stats.get("views") is not None:
                views = int(stats.get("views"))
        videos.append(
            {
                "video_id": video_id,
                "title": entry.findtext("atom:title", default="", namespaces=_NS),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "published": datetime.fromisoformat(published) if published else None,
                "thumbnail": thumbnail,
                "views": views,
            }
        )
    return {
        "channel_title": root.findtext("atom:title", default="", namespaces=_NS),
        "videos": videos,
    }


_MAX_WORKERS = 8


def _channel_result(channel: str, n: int) -> dict:
    norm = _normalize(channel)
    try:
        channel_id = resolve_channel_id(channel)
        feed = _parse_feed(_fetch(FEED_URL.format(channel_id=channel_id)), n)
        return {"channel": norm, "channel_id": channel_id, **feed}
    except Exception as e:
        return {"channel": norm, "error": str(e)}


def latest_videos(channels: list[str], n: int = 5) -> list[dict]:
    if not channels:
        return []
    n = max(1, min(n, 15))
    workers = min(_MAX_WORKERS, len(channels))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(lambda c: _channel_result(c, n), channels))


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
    args = parser.parse_args(argv)

    results = latest_videos(args.channels, n=args.n)

    if args.as_json:
        print(json.dumps(results, default=_json_default, indent=2))
    else:
        for r in results:
            if "error" in r:
                print(f"{r['channel']}: error: {r['error']}")
                continue
            print(f"{r['channel_title']} ({r['channel']})")
            for v in r["videos"]:
                date = v["published"].date().isoformat() if v["published"] else "?"
                views = f"{v['views']:,} views" if v["views"] is not None else "views n/a"
                print(f"  [{date}] {v['title']} — {views}")
                print(f"          {v['url']}")
            print()

    return 1 if any("error" in r for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
