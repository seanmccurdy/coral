"""Search YouTube for one-off videos matching keyword queries.

Complements youtube_latest (which tracks known channels): finds relevant
videos from channels you don't follow, with recency / view-count /
subscriber-count filters. Rides the same unofficial youtubei surface as
transcript fetching — the most breakage-prone part of coral.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from youtube_latest import (
    _MAX_WORKERS,
    _CACHE_DIR,
    _fetch,
    _fetch_transcript,
    _json_default,
    _open_cache,
    _post_json,
    _read_channels_file,
    PLAYER_URL,
    resolve_channel_id,
)

SEARCH_URL = "https://www.youtube.com/youtubei/v1/search"
# The WEB client works unauthenticated for search and returns microformat
# (exact publishDate) on the player endpoint; the ANDROID client (used for
# transcripts) returns neither.
_WEB_CLIENT = {"clientName": "WEB", "clientVersion": "2.20250101.00.00"}
# "sp" filter params: results restricted to type=video plus an upload-date
# window. Chosen from `days`, then the window is re-applied precisely on the
# exact publish dates (search's own filter is coarse).
_DATE_PARAMS = ((7, "EgQIAxAB"), (31, "EgQIBBAB"))  # week, month
_YEAR_PARAMS = "EgQIBRAB"

# Video metadata (views drift) and channel pages (subscriber counts drift)
# get a short TTL, unlike the 1-year transcript cache.
_META_TTL_SECONDS = 7 * 24 * 60 * 60
_VIDEO_META_CACHE_DIR = _CACHE_DIR.parent / "videometa"
_CHANNEL_CACHE_DIR = _CACHE_DIR.parent / "channels"

_SUBS_RE = re.compile(r'"([\d.,]+[KMB]?)\s+subscribers"')
_HANDLE_RE = re.compile(r'"canonicalBaseUrl":"/(@[^"]+)"')


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _date_params(days: int) -> str:
    for limit, params in _DATE_PARAMS:
        if days <= limit:
            return params
    return _YEAR_PARAMS


def _walk(node, key: str, out: list) -> None:
    if isinstance(node, dict):
        if key in node:
            out.append(node[key])
        for v in node.values():
            _walk(v, key, out)
    elif isinstance(node, list):
        for v in node:
            _walk(v, key, out)


def _search_query(query: str, days: int, limit: int) -> list[dict]:
    """One search request; returns raw rows (video_id, title, channel)."""
    data = _post_json(
        SEARCH_URL,
        {"context": {"client": _WEB_CLIENT}, "query": query, "params": _date_params(days)},
    )
    renderers: list = []
    _walk(data, "videoRenderer", renderers)
    rows = []
    for v in renderers[:limit]:
        owner = v.get("ownerText", {}).get("runs", [{}])[0]
        rows.append(
            {
                "video_id": v.get("videoId"),
                "title": "".join(r.get("text", "") for r in v.get("title", {}).get("runs", [])),
                "channel_name": owner.get("text"),
                "channel_id": owner.get("navigationEndpoint", {})
                .get("browseEndpoint", {})
                .get("browseId"),
            }
        )
    return rows


def _video_meta(video_id: str, use_cache: bool = True) -> dict:
    """Exact publish date, views, description, thumbnail via the player
    endpoint (WEB client). Cached with a short TTL since views drift."""
    cache = _open_cache(str(_VIDEO_META_CACHE_DIR))
    if use_cache:
        cached = cache.get(video_id)
        if cached is not None:
            return cached
    p = _post_json(PLAYER_URL, {"context": {"client": _WEB_CLIENT}, "videoId": video_id})
    vd = p.get("videoDetails", {})
    mf = p.get("microformat", {}).get("playerMicroformatRenderer", {})
    thumbs = vd.get("thumbnail", {}).get("thumbnails", [])
    meta = {
        "published": mf.get("publishDate"),  # ISO string or None
        "views": int(vd["viewCount"]) if vd.get("viewCount") else None,
        "description": vd.get("shortDescription"),
        "thumbnail": thumbs[-1].get("url") if thumbs else None,
    }
    if use_cache:
        try:
            cache.set(video_id, meta, expire=_META_TTL_SECONDS)
        except Exception:
            pass
    return meta


def _parse_subscriber_count(text: str) -> int | None:
    m = re.fullmatch(r"([\d.,]+)\s*([KMB]?)", text.strip())
    if m is None:
        return None
    number = float(m.group(1).replace(",", ""))
    factor = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[m.group(2)]
    return int(number * factor)


def _channel_info(channel_id: str, use_cache: bool = True) -> dict:
    """Subscriber count (YouTube's public rounded figure) and @handle from
    the channel page. Cached with a short TTL."""
    cache = _open_cache(str(_CHANNEL_CACHE_DIR))
    if use_cache:
        cached = cache.get(channel_id)
        if cached is not None:
            return cached
    info = {"subscribers": None, "handle": None}
    try:
        html = _fetch(f"https://www.youtube.com/channel/{channel_id}")
        m = _SUBS_RE.search(html)
        if m:
            info["subscribers"] = _parse_subscriber_count(m.group(1))
        m = _HANDLE_RE.search(html)
        if m:
            info["handle"] = m.group(1)
    except Exception:
        pass  # unknown channel info must not break the search
    if use_cache and (info["subscribers"] is not None or info["handle"] is not None):
        try:
            cache.set(channel_id, info, expire=_META_TTL_SECONDS)
        except Exception:
            pass
    return info


def _resolve_excluded(exclude_channels) -> set[str]:
    excluded = set()
    for c in exclude_channels or []:
        try:
            excluded.add(resolve_channel_id(c))
        except Exception:
            pass  # an unresolvable exclusion entry just doesn't exclude
    return excluded


def search_videos(
    queries: list[str],
    days: int = 30,
    limit: int = 20,
    min_views: int = 0,
    min_subs: int = 0,
    exclude_channels: list[str] | None = None,
    include_transcripts: bool = False,
    use_cache: bool = True,
) -> list[dict]:
    """Return a flat list with one dict per video found for the queries,
    deduped across queries (first query wins), filtered to the last `days`
    days, `min_views` views, and `min_subs` channel subscribers. A failed
    query contributes exactly one element: {"query": ..., "error": "<msg>"}.
    """
    if not queries:
        return []
    excluded = _resolve_excluded(exclude_channels)

    flat: list[dict] = []
    seen: set[str] = set()
    for query in queries:
        try:
            rows = _search_query(query, days, limit)
        except Exception as e:
            flat.append({"query": query, "error": str(e)})
            continue
        for row in rows:
            vid = row["video_id"]
            if not vid or vid in seen or row["channel_id"] in excluded:
                continue
            seen.add(vid)
            row["query"] = query
            flat.append(row)

    candidates = [r for r in flat if "error" not in r]
    if candidates:
        with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(candidates))) as ex:
            metas = list(
                ex.map(lambda r: _video_meta(r["video_id"], use_cache=use_cache), candidates)
            )
        cutoff = _now() - timedelta(days=days)
        for row, meta in zip(candidates, metas):
            published = meta["published"]
            row["published"] = datetime.fromisoformat(published) if published else None
            row["views"] = meta["views"]
            row["description"] = meta["description"]
            row["thumbnail"] = meta["thumbnail"]
        # Filters fail open on unknown values: a row with no exact date or
        # view count is kept rather than silently guessed about.
        candidates = [
            r
            for r in candidates
            if (r["published"] is None or r["published"] >= cutoff)
            and (r["views"] is None or r["views"] >= min_views)
        ]

    if candidates:
        channel_ids = {r["channel_id"] for r in candidates if r["channel_id"]}
        infos = {}
        with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, max(len(channel_ids), 1))) as ex:
            for cid, info in zip(
                channel_ids, ex.map(lambda c: _channel_info(c, use_cache=use_cache), channel_ids)
            ):
                infos[cid] = info
        for r in candidates:
            info = infos.get(r["channel_id"], {"subscribers": None, "handle": None})
            r["channel_subscribers"] = info["subscribers"]
            r["channel_handle"] = info["handle"]
        candidates = [
            r
            for r in candidates
            if r["channel_subscribers"] is None or r["channel_subscribers"] >= min_subs
        ]

    if include_transcripts and candidates:
        with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(candidates))) as ex:
            transcripts = ex.map(
                lambda r: _fetch_transcript(r["video_id"], use_cache=use_cache), candidates
            )
            for r, (text, lang) in zip(candidates, transcripts):
                r["transcript"] = text
                r["transcript_language"] = lang

    kept = {id(r) for r in candidates}
    ordered_keys = [
        "query",
        "channel_handle",
        "channel_id",
        "channel_name",
        "channel_subscribers",
        "video_id",
        "title",
        "description",
        "url",
        "published",
        "thumbnail",
        "views",
    ]
    results = []
    for r in flat:
        if "error" in r:
            results.append(r)
            continue
        if id(r) not in kept:
            continue
        r["url"] = f"https://www.youtube.com/watch?v={r['video_id']}"
        ordered = {k: r.get(k) for k in ordered_keys}
        if include_transcripts:
            ordered["transcript"] = r.get("transcript")
            ordered["transcript_language"] = r.get("transcript_language")
        results.append(ordered)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search YouTube for recent one-off videos matching queries."
    )
    parser.add_argument("queries", nargs="*", help="search queries")
    parser.add_argument(
        "-q",
        "--queries-file",
        help="text file with one query per line (# comments and blanks ignored)",
    )
    parser.add_argument("--days", type=int, default=30, help="recency window in days")
    parser.add_argument("--limit", type=int, default=20, help="max results per query")
    parser.add_argument("--min-views", type=int, default=0, help="minimum video views")
    parser.add_argument(
        "--min-subs", type=int, default=0, help="minimum channel subscribers"
    )
    parser.add_argument(
        "--exclude-file",
        help="channels file (e.g. channels.txt) whose videos are dropped",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    parser.add_argument(
        "--transcripts",
        action="store_true",
        dest="include_transcripts",
        help="also fetch each video's transcript",
    )
    parser.add_argument(
        "--no-cache", action="store_false", dest="use_cache", help="bypass caches"
    )
    args = parser.parse_args(argv)

    queries = list(args.queries)
    if args.queries_file:
        queries.extend(_read_channels_file(args.queries_file))
    if not queries:
        parser.error("provide at least one query or --queries-file")

    exclude = _read_channels_file(args.exclude_file) if args.exclude_file else None
    results = search_videos(
        queries,
        days=args.days,
        limit=args.limit,
        min_views=args.min_views,
        min_subs=args.min_subs,
        exclude_channels=exclude,
        include_transcripts=args.include_transcripts,
        use_cache=args.use_cache,
    )

    if args.as_json:
        print(json.dumps(results, default=_json_default, indent=2))
    else:
        current_query = None
        for r in results:
            if "error" in r:
                if current_query is not None:
                    print()
                    current_query = None
                print(f"{r['query']}: error: {r['error']}")
                continue
            if r["query"] != current_query:
                if current_query is not None:
                    print()
                print(f"# {r['query']}")
                current_query = r["query"]
            date = r["published"].date().isoformat() if r["published"] else "?"
            views = f"{r['views']:,} views" if r["views"] is not None else "views n/a"
            subs = (
                f"{r['channel_subscribers']:,} subs"
                if r["channel_subscribers"] is not None
                else "subs n/a"
            )
            print(f"  [{date}] {r['title']} — {views}")
            print(f"          {r['channel_name']} ({subs}) | {r['url']}")

    return 1 if any("error" in r for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
