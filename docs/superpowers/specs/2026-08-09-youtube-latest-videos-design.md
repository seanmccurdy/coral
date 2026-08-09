# YouTube Latest Videos — Design

**Date:** 2026-08-09
**Status:** Approved approach A (zero-dependency module + small CLI), uv for environment management

## Purpose

A Python function that takes a list of YouTube channel handles and returns
info on each channel's latest video posts, without requiring a YouTube API
key.

## Data source

YouTube's per-channel Atom feed (`channel_id=UC...`) mixes long-form videos
with Shorts/clips, so "latest video" from that feed alone can be wrong for
Shorts-heavy channels. Instead, the primary source is the channel's
long-form-only "uploads" playlist feed, derived from the channel ID by
swapping the `UC` prefix for `UULF`:

`https://www.youtube.com/feeds/videos.xml?playlist_id=UULF<channel-id-suffix>`

This matches what the channel's "Videos" tab shows (verified live against
`@TheDiaryOfACEO`). If fetching the UULF feed raises, or it parses to zero
videos (some channels lack this playlist), we fall back to the mixed
channel feed:

`https://www.youtube.com/feeds/videos.xml?channel_id=UC...`

- Both are free, no API key, no quota.
- Provide up to ~15 most recent videos per channel/playlist.
- Per video: video ID, title, link, published/updated timestamps, thumbnail
  URL, description snippet, and view count (`media:statistics`).
- Channel-feed `<title>` is the channel name; playlist-feed `<title>` is the
  playlist name ("Videos") — the channel name there is in
  `<author><name>`. Feed parsing prefers `author/name` when present, falling
  back to root `title`, so `channel_title` is correct for either feed kind.

## Module: `youtube_latest.py`

Runtime dependencies: **none** (stdlib only: `urllib.request`,
`xml.etree.ElementTree`, `concurrent.futures`, `re`, `json`, `argparse`,
`datetime`). Project managed with uv (`pyproject.toml`); dev dependency:
`pytest`.

### `resolve_channel_id(handle: str) -> str`

- Accepts `@name` or bare `name`; normalizes to `@name`.
- If input already looks like a channel ID (`UC` + 22 chars), returns it
  unchanged.
- Fetches `https://www.youtube.com/@<name>` and extracts the `UC...` ID from
  the page's `og:url` / `"channelId"` meta content.
- Raises `ChannelNotFoundError` (module-level exception) when the handle
  doesn't resolve (HTTP 404 or no ID found in page).
- Results cached per-process (`functools.lru_cache`).

### `latest_videos(channels: list[str], n: int = 5, include_shorts: bool = False) -> list[dict]`

- `include_shorts=False` (default): fetch the long-form UULF playlist feed
  (with channel-feed fallback as described above) — results match the
  channel's "Videos" tab.
- `include_shorts=True`: fetch the mixed `channel_id=UC...` feed directly —
  Shorts and clips appear alongside videos.

- Returns a **flat list with one dict per video** (not one dict per
  channel). Channels appear in input order; within a channel, videos are
  newest-first:

```python
[
    {
        "channel": "@mkbhd",          # as passed in (normalized)
        "channel_id": "UC...",
        "channel_title": "Marques Brownlee",
        "video_id": "abc123",
        "title": "...",
        "url": "https://www.youtube.com/watch?v=abc123",
        "published": datetime(...),   # timezone-aware
        "thumbnail": "https://i.ytimg.com/...",
        "views": 123456,              # int or None if absent
    },
    ...  # up to n entries per channel, newest first, then the next channel's videos
]
```

- `n` clamped to what the feed provides (~15 max), applied per channel.
- Channels fetched concurrently via `ThreadPoolExecutor` (bounded workers).
- **Per-channel error isolation:** a channel that fails (unknown handle,
  network error, malformed feed) contributes exactly **one** element,
  `{"channel": ..., "error": "<message>"}`, instead of raising; other
  channels are unaffected.

## CLI

`python youtube_latest.py @mkbhd @veritasium -n 3 [--json] [--include-shorts]`

- `--include-shorts`: pass `include_shorts=True` (mixed feed, Shorts
  included). Default is long-form only.

- Default output: readable summary, still visually grouped by channel (a
  channel header is printed once, followed by its videos) even though the
  underlying data is a flat list — the CLI tracks channel changes while
  iterating.
- `--json`: prints the flat list as a JSON array (datetimes serialized as
  ISO 8601).
- Exit code 0 if no element has `"error"`, 1 if any element does.

## Testing

- `pytest` with mocked HTTP (saved sample channel page + sample Atom feed as
  fixture files) so tests run offline.
- Cover: handle normalization, ID passthrough, resolution failure, feed
  parsing (fields, ordering, `n` clamping), per-channel error isolation,
  JSON serialization.

## Out of scope (YAGNI)

- Arbitrary playlists (beyond the UULF long-form playlist), live-stream
  filtering, pagination beyond the feed's ~15 items, persistent caching,
  YouTube Data API fallback.
