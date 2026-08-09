# YouTube Latest Videos — Design

**Date:** 2026-08-09
**Status:** Approved approach A (zero-dependency module + small CLI), uv for environment management

## Purpose

A Python function that takes a list of YouTube channel handles and returns
info on each channel's latest video posts, without requiring a YouTube API
key.

## Data source

YouTube's per-channel Atom feed:
`https://www.youtube.com/feeds/videos.xml?channel_id=UC...`

- Free, no API key, no quota.
- Provides up to ~15 most recent videos per channel.
- Per video: video ID, title, link, published/updated timestamps, thumbnail
  URL, description snippet, and view count (`media:statistics`).

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

### `latest_videos(channels: list[str], n: int = 5) -> list[dict]`

- One result dict per input channel, in input order:

```python
{
    "channel": "@mkbhd",          # as passed in (normalized)
    "channel_id": "UC...",
    "channel_title": "Marques Brownlee",
    "videos": [
        {
            "video_id": "abc123",
            "title": "...",
            "url": "https://www.youtube.com/watch?v=abc123",
            "published": datetime(...),   # timezone-aware
            "thumbnail": "https://i.ytimg.com/...",
            "views": 123456,              # int or None if absent
        },
        ...  # up to n entries, newest first
    ],
}
```

- `n` clamped to what the feed provides (~15 max).
- Channels fetched concurrently via `ThreadPoolExecutor` (bounded workers).
- **Per-channel error isolation:** a channel that fails (unknown handle,
  network error, malformed feed) yields
  `{"channel": ..., "error": "<message>"}` instead of raising; other
  channels are unaffected.

## CLI

`python youtube_latest.py @mkbhd @veritasium -n 3 [--json]`

- Default output: readable per-channel summary (title, date, URL).
- `--json`: JSON array (datetimes serialized as ISO 8601).
- Exit code 0 if all channels succeeded, 1 if any had errors.

## Testing

- `pytest` with mocked HTTP (saved sample channel page + sample Atom feed as
  fixture files) so tests run offline.
- Cover: handle normalization, ID passthrough, resolution failure, feed
  parsing (fields, ordering, `n` clamping), per-channel error isolation,
  JSON serialization.

## Out of scope (YAGNI)

- Playlists, Shorts/live filtering, pagination beyond the feed's ~15 items,
  persistent caching, YouTube Data API fallback.
