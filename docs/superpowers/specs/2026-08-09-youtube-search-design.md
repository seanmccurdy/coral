# YouTube One-Off Video Search — Design

**Date:** 2026-08-09
**Status:** Approved (approach A: InnerTube search)

## Purpose

A second search mode for coral: discover relevant one-off videos posted by
channels *outside* the subscribed `channels.txt` list, driven by
user-maintained keyword queries. Complements `latest_videos` (which covers
the known channels).

## Module: `youtube_search.py`

Separate module so `youtube_latest.py` stays focused on channels. Imports
coral's existing plumbing from `youtube_latest`: `_fetch`, `_post_json`,
`_fetch_transcript`, `_read_channels_file`, `resolve_channel_id`,
`_json_default`, `_open_cache`. Runtime deps unchanged (`diskcache`).

### `search_videos(queries, days=30, limit=20, min_views=0, min_subs=0, exclude_channels=None, include_transcripts=False, use_cache=True) -> list[dict]`

Data flow, in order (cheapest first, transcripts last):

1. **Search** — one POST per query to the unofficial
   `youtubei/v1/search` endpoint (same `youtubei` surface the transcript
   fetch uses), with YouTube's own upload-date filter param chosen from
   `days` (≤7 → week, ≤31 → month, else year) to pre-narrow server-side.
   Top ~`limit` (default 20) video results per query.
2. **Dedupe** across queries by `video_id` — first query wins; the winning
   query is recorded in the row's `query` key.
3. **Exclusion** — drop hits whose `channel_id` resolves to any channel in
   `exclude_channels` (a list of handles/IDs, e.g. from `channels.txt`).
4. **Exact-date + view enrichment** — one player-endpoint call per
   surviving video (the same call transcripts use) for the exact
   `published` date and exact `views`; then the `days` window is applied
   precisely (search's "2 weeks ago" text is too coarse). Enrichment
   results are cached (video metadata cache, 7-day TTL — views drift, so
   not the 1-year transcript TTL).
5. **min_views filter** — on the exact count.
6. **min_subs filter** — one channel-page fetch per *unique* surviving
   channel; subscriber counts are YouTube's public rounded figures
   ("1.23M"), parsed to an int. Cached 7 days in a `channels` cache
   namespace.
7. **Transcripts** (opt-in) — via the existing `_fetch_transcript`
   machinery and 1-year cache, only for rows that survived all filters.

### Output schema

Same MECE flat-list-of-videos schema as `latest_videos`, plus:

- `query` — which search term surfaced the row
- `channel_subscribers` — rounded subscriber count as an int (`None` if
  unparseable)

A failed query contributes exactly one `{"query": ..., "error": ...}`
element; per-query isolation mirrors `latest_videos`' per-channel
isolation. Rows that merely fail a filter are dropped silently (that is
the filter's job), but enrichment failures (no exact date obtainable)
keep the row with `published: None` rather than guessing.

## CLI

`uv run python youtube_search.py "VO2 max training" [-q queries.txt] [--days 30] [--limit 20] [--min-views 10000] [--min-subs 50000] [--exclude-file channels.txt] [--json] [--transcripts] [--no-cache]`

- Positional queries and/or `-q/--queries-file` (one query per line, `#`
  comments and blanks ignored — same format rules as `channels.txt`);
  at least one required (argparse error, exit 2).
- Human output groups by query; `--json` prints the flat list; exit 1 if
  any element has `"error"`.
- All filters default off/permissive: `--days 30`, `--limit 20`,
  `--min-views 0`, `--min-subs 0`, no exclusion unless given.

## Testing

Offline as always: mocked `_post_json`/`_fetch` with fixture responses
(trimmed real search response, player response, channel page). Cover:
query-file parsing, dedupe-across-queries, date-window filtering,
exclusion, min_views, min_subs (incl. "1.23M"-style parsing), transcript
opt-in, per-query error isolation, CLI flags. Live smoke test at the end.

## Caveats

Rides the same unofficial `youtubei` surface as transcripts — the most
breakage-prone part of coral. Subscriber counts are rounded by YouTube;
thresholds operate on those public figures.

## Out of scope (YAGNI)

Continuation paging beyond ~20 results/query, relevance scoring, automatic
topic derivation from the subscribed channels, notification/diffing between
runs.
