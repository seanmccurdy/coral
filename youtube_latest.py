"""Latest YouTube videos for a list of channels, via public Atom feeds."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from functools import lru_cache

CHANNEL_URL = "https://www.youtube.com/{handle}"
_CHANNEL_ID_RE = re.compile(r"UC[0-9A-Za-z_-]{22}")
_USER_AGENT = "Mozilla/5.0 (compatible; youtube-latest/0.1)"


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
