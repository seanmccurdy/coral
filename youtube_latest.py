"""Latest YouTube videos for a list of channels, via public Atom feeds."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
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


@lru_cache(maxsize=None)
def resolve_channel_id(handle: str) -> str:
    if _is_channel_id(handle):
        return handle
    h = handle if handle.startswith("@") else "@" + handle
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
