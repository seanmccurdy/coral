# YouTube Latest Videos Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A zero-dependency Python module `youtube_latest.py` whose `latest_videos(channels, n)` returns recent-video info for a list of YouTube channel handles via YouTube's public Atom feeds, plus a small CLI.

**Architecture:** One flat module at the repo root. Handle → channel ID resolution scrapes the `UC...` ID out of the channel page HTML (cached per-process). Video data comes from `https://www.youtube.com/feeds/videos.xml?channel_id=...`, parsed with stdlib `xml.etree`. Channels are fetched concurrently with `ThreadPoolExecutor`; failures are isolated per channel. Tests mock the single HTTP helper `_fetch` and use saved fixture files, so they run offline.

**Tech Stack:** Python ≥3.11 stdlib only at runtime. uv for env management; pytest as the only dev dependency.

## Global Constraints

- Runtime dependencies: **none** (stdlib only). Dev dependency: `pytest` only.
- Python ≥ 3.11 (needed for `datetime.fromisoformat` on RFC-3339 strings with offsets).
- All HTTP goes through the single helper `youtube_latest._fetch(url)` — tests monkeypatch only this.
- `n` is clamped to 1..15 (the feed provides at most ~15 entries).
- Per-channel error isolation: a failing channel yields `{"channel": ..., "error": "<msg>"}`; never raises out of `latest_videos`.
- Run tests with `uv run pytest -v` from the repo root.

---

### Task 1: Project scaffold + `resolve_channel_id`

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `youtube_latest.py`
- Create: `tests/fixtures/channel_page.html`
- Create: `tests/conftest.py`
- Test: `tests/test_resolve.py`

**Interfaces:**
- Produces: `resolve_channel_id(handle: str) -> str` (raises `ChannelNotFoundError`), `ChannelNotFoundError(Exception)`, `_fetch(url: str) -> str`, `_is_channel_id(s: str) -> bool`. Later tasks import all of these from `youtube_latest`.

- [ ] **Step 1: Scaffold the project**

Create `pyproject.toml`:

```toml
[project]
name = "youtube-latest"
version = "0.1.0"
description = "Latest YouTube videos for a list of channels, via public Atom feeds"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = ["pytest>=8"]
```

Create `.gitignore`:

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

Run: `uv sync` (creates `.venv` and `uv.lock`, installs pytest).

- [ ] **Step 2: Create the channel-page fixture**

Create `tests/fixtures/channel_page.html` (trimmed to the parts the resolver reads — real channel pages embed the ID exactly like this):

```html
<!DOCTYPE html>
<html>
<head>
<meta property="og:url" content="https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ">
<link rel="canonical" href="https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ">
</head>
<body>
<script>var ytInitialData = {"metadata":{"channelMetadataRenderer":{"title":"Marques Brownlee","channelId":"UCBJycsmduvYEL83R_U4JriQ"}}};</script>
</body>
</html>
```

- [ ] **Step 3: Create `tests/conftest.py`**

`resolve_channel_id` is `lru_cache`d; clear it between tests so mocks don't leak:

```python
import pytest

import youtube_latest


@pytest.fixture(autouse=True)
def clear_resolve_cache():
    youtube_latest.resolve_channel_id.cache_clear()
    yield
    youtube_latest.resolve_channel_id.cache_clear()
```

- [ ] **Step 4: Write the failing tests**

Create `tests/test_resolve.py`:

```python
import urllib.error
from pathlib import Path

import pytest

import youtube_latest
from youtube_latest import ChannelNotFoundError, resolve_channel_id

FIXTURES = Path(__file__).parent / "fixtures"
MKBHD_ID = "UCBJycsmduvYEL83R_U4JriQ"


def mock_fetch(monkeypatch, body=None, exc=None):
    calls = []

    def fake_fetch(url):
        calls.append(url)
        if exc is not None:
            raise exc
        return body

    monkeypatch.setattr(youtube_latest, "_fetch", fake_fetch)
    return calls


def test_resolves_handle_from_channel_page(monkeypatch):
    calls = mock_fetch(monkeypatch, body=(FIXTURES / "channel_page.html").read_text())
    assert resolve_channel_id("@mkbhd") == MKBHD_ID
    assert calls == ["https://www.youtube.com/@mkbhd"]


def test_bare_name_is_normalized_to_handle(monkeypatch):
    calls = mock_fetch(monkeypatch, body=(FIXTURES / "channel_page.html").read_text())
    assert resolve_channel_id("mkbhd") == MKBHD_ID
    assert calls == ["https://www.youtube.com/@mkbhd"]


def test_channel_id_passes_through_without_fetch(monkeypatch):
    calls = mock_fetch(monkeypatch, body="should not be fetched")
    assert resolve_channel_id(MKBHD_ID) == MKBHD_ID
    assert calls == []


def test_unknown_handle_404_raises(monkeypatch):
    err = urllib.error.HTTPError("u", 404, "Not Found", None, None)
    mock_fetch(monkeypatch, exc=err)
    with pytest.raises(ChannelNotFoundError):
        resolve_channel_id("@nosuchchannelxyz")


def test_page_without_id_raises(monkeypatch):
    mock_fetch(monkeypatch, body="<html><body>consent wall</body></html>")
    with pytest.raises(ChannelNotFoundError):
        resolve_channel_id("@mkbhd")


def test_resolution_is_cached(monkeypatch):
    calls = mock_fetch(monkeypatch, body=(FIXTURES / "channel_page.html").read_text())
    resolve_channel_id("@mkbhd")
    resolve_channel_id("@mkbhd")
    assert len(calls) == 1
```

- [ ] **Step 5: Run tests to verify they fail**

Run: `uv run pytest tests/test_resolve.py -v`
Expected: collection error / FAIL with `ModuleNotFoundError: No module named 'youtube_latest'`.

- [ ] **Step 6: Write the implementation**

Create `youtube_latest.py`:

```python
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
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest tests/test_resolve.py -v`
Expected: 6 passed.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml uv.lock .gitignore youtube_latest.py tests/
git commit -m "feat: project scaffold and channel handle resolution"
```

---

### Task 2: Atom feed parsing

**Files:**
- Modify: `youtube_latest.py`
- Create: `tests/fixtures/feed.xml`
- Test: `tests/test_feed.py`

**Interfaces:**
- Consumes: nothing from Task 1 (pure parsing).
- Produces: `_parse_feed(xml_text: str, n: int) -> dict` returning `{"channel_title": str, "videos": list[dict]}`; each video dict has keys `video_id: str`, `title: str`, `url: str`, `published: datetime | None` (tz-aware), `thumbnail: str | None`, `views: int | None`. Task 3 calls `_parse_feed`.

- [ ] **Step 1: Create the feed fixture**

Create `tests/fixtures/feed.xml` — a real-shaped YouTube Atom feed with 3 entries, newest first (YouTube's feed order). Note `media:statistics` lives at `media:group/media:community/media:statistics`, and the third entry deliberately omits the community block to exercise `views=None`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"
      xmlns:media="http://search.yahoo.com/mrss/"
      xmlns="http://www.w3.org/2005/Atom">
  <title>Marques Brownlee</title>
  <entry>
    <id>yt:video:vid00000001</id>
    <yt:videoId>vid00000001</yt:videoId>
    <title>Newest Video</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=vid00000001"/>
    <published>2026-08-08T15:00:00+00:00</published>
    <media:group>
      <media:title>Newest Video</media:title>
      <media:thumbnail url="https://i.ytimg.com/vi/vid00000001/hqdefault.jpg" width="480" height="360"/>
      <media:community>
        <media:statistics views="1234567"/>
      </media:community>
    </media:group>
  </entry>
  <entry>
    <id>yt:video:vid00000002</id>
    <yt:videoId>vid00000002</yt:videoId>
    <title>Middle Video</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=vid00000002"/>
    <published>2026-08-05T12:30:00+00:00</published>
    <media:group>
      <media:title>Middle Video</media:title>
      <media:thumbnail url="https://i.ytimg.com/vi/vid00000002/hqdefault.jpg" width="480" height="360"/>
      <media:community>
        <media:statistics views="89000"/>
      </media:community>
    </media:group>
  </entry>
  <entry>
    <id>yt:video:vid00000003</id>
    <yt:videoId>vid00000003</yt:videoId>
    <title>Oldest Video</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=vid00000003"/>
    <published>2026-08-01T09:00:00+00:00</published>
    <media:group>
      <media:title>Oldest Video</media:title>
      <media:thumbnail url="https://i.ytimg.com/vi/vid00000003/hqdefault.jpg" width="480" height="360"/>
    </media:group>
  </entry>
</feed>
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_feed.py`:

```python
from datetime import datetime, timezone
from pathlib import Path

from youtube_latest import _parse_feed

FEED = (Path(__file__).parent / "fixtures" / "feed.xml").read_text()


def test_parses_channel_title_and_all_fields():
    result = _parse_feed(FEED, n=15)
    assert result["channel_title"] == "Marques Brownlee"
    v = result["videos"][0]
    assert v == {
        "video_id": "vid00000001",
        "title": "Newest Video",
        "url": "https://www.youtube.com/watch?v=vid00000001",
        "published": datetime(2026, 8, 8, 15, 0, 0, tzinfo=timezone.utc),
        "thumbnail": "https://i.ytimg.com/vi/vid00000001/hqdefault.jpg",
        "views": 1234567,
    }


def test_preserves_newest_first_order():
    ids = [v["video_id"] for v in _parse_feed(FEED, n=15)["videos"]]
    assert ids == ["vid00000001", "vid00000002", "vid00000003"]


def test_n_limits_entries():
    assert len(_parse_feed(FEED, n=2)["videos"]) == 2


def test_missing_statistics_gives_none_views():
    videos = _parse_feed(FEED, n=15)["videos"]
    assert videos[2]["views"] is None
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_feed.py -v`
Expected: FAIL with `ImportError: cannot import name '_parse_feed'`.

- [ ] **Step 4: Implement `_parse_feed`**

Add to `youtube_latest.py` (new imports at the top with the existing ones):

```python
import xml.etree.ElementTree as ET
from datetime import datetime
```

```python
FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_feed.py -v`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add youtube_latest.py tests/fixtures/feed.xml tests/test_feed.py
git commit -m "feat: parse YouTube Atom feeds into video dicts"
```

---

### Task 3: `latest_videos` with concurrency and error isolation

**Files:**
- Modify: `youtube_latest.py`
- Test: `tests/test_latest_videos.py`

**Interfaces:**
- Consumes: `resolve_channel_id`, `_fetch`, `_is_channel_id`, `_parse_feed`, `FEED_URL`, `CHANNEL_URL`, `ChannelNotFoundError` from Tasks 1–2.
- Produces: `latest_videos(channels: list[str], n: int = 5) -> list[dict]`. Success dicts: `{"channel", "channel_id", "channel_title", "videos"}`; failure dicts: `{"channel", "error"}`. Task 4 (CLI) calls this.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_latest_videos.py`:

```python
from pathlib import Path

import youtube_latest
from youtube_latest import latest_videos

FIXTURES = Path(__file__).parent / "fixtures"
MKBHD_ID = "UCBJycsmduvYEL83R_U4JriQ"


def route_fetch(monkeypatch, fail_feeds=()):
    """_fetch stub: channel pages resolve via the HTML fixture, feeds via feed.xml."""
    page = (FIXTURES / "channel_page.html").read_text()
    feed = (FIXTURES / "feed.xml").read_text()

    def fake_fetch(url):
        if "feeds/videos.xml" in url:
            cid = url.split("channel_id=")[1]
            if cid in fail_feeds:
                raise OSError("connection reset")
            return feed
        if url == "https://www.youtube.com/@nosuchchannel":
            return "<html>no id here</html>"
        return page

    monkeypatch.setattr(youtube_latest, "_fetch", fake_fetch)


def test_returns_one_result_per_channel_in_input_order(monkeypatch):
    route_fetch(monkeypatch)
    results = latest_videos(["@mkbhd", MKBHD_ID], n=2)
    assert [r["channel"] for r in results] == ["@mkbhd", MKBHD_ID]
    for r in results:
        assert r["channel_id"] == MKBHD_ID
        assert r["channel_title"] == "Marques Brownlee"
        assert len(r["videos"]) == 2


def test_bare_name_normalized_in_result(monkeypatch):
    route_fetch(monkeypatch)
    assert latest_videos(["mkbhd"], n=1)[0]["channel"] == "@mkbhd"


def test_bad_handle_isolated_as_error(monkeypatch):
    route_fetch(monkeypatch)
    results = latest_videos(["@nosuchchannel", "@mkbhd"], n=1)
    assert "error" in results[0] and "videos" not in results[0]
    assert results[1]["channel_title"] == "Marques Brownlee"


def test_feed_fetch_failure_isolated_as_error(monkeypatch):
    route_fetch(monkeypatch, fail_feeds={MKBHD_ID})
    results = latest_videos(["@mkbhd"], n=1)
    assert results[0]["error"] == "connection reset"


def test_n_is_clamped(monkeypatch):
    route_fetch(monkeypatch)
    assert len(latest_videos(["@mkbhd"], n=99)[0]["videos"]) == 3  # fixture has 3
    assert len(latest_videos(["@mkbhd"], n=0)[0]["videos"]) == 1


def test_empty_channel_list(monkeypatch):
    route_fetch(monkeypatch)
    assert latest_videos([]) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_latest_videos.py -v`
Expected: FAIL with `ImportError: cannot import name 'latest_videos'`.

- [ ] **Step 3: Implement `latest_videos`**

Add to `youtube_latest.py` (new import: `from concurrent.futures import ThreadPoolExecutor`):

```python
_MAX_WORKERS = 8


def _normalize(channel: str) -> str:
    if _is_channel_id(channel) or channel.startswith("@"):
        return channel
    return "@" + channel


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
```

- [ ] **Step 4: Run the full suite**

Run: `uv run pytest -v`
Expected: all tests pass (Tasks 1–3: 16 tests).

- [ ] **Step 5: Commit**

```bash
git add youtube_latest.py tests/test_latest_videos.py
git commit -m "feat: latest_videos with concurrent fetch and per-channel error isolation"
```

---

### Task 4: CLI

**Files:**
- Modify: `youtube_latest.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `latest_videos` from Task 3.
- Produces: `main(argv: list[str] | None = None) -> int` and an `if __name__ == "__main__"` guard. Usage: `uv run python youtube_latest.py @mkbhd @veritasium -n 3 [--json]`. Exit 0 if all channels succeeded, 1 if any errored.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_cli.py`:

```python
import json

from tests.test_latest_videos import route_fetch
from youtube_latest import main


def test_human_output_lists_videos(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", "-n", "2"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Marques Brownlee" in out
    assert "Newest Video" in out
    assert "https://www.youtube.com/watch?v=vid00000001" in out


def test_json_output_is_valid_and_iso_dates(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@mkbhd", "-n", "1", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data[0]["videos"][0]["published"] == "2026-08-08T15:00:00+00:00"


def test_exit_code_1_when_any_channel_errors(monkeypatch, capsys):
    route_fetch(monkeypatch)
    code = main(["@nosuchchannel", "@mkbhd"])
    out = capsys.readouterr().out
    assert code == 1
    assert "error" in out.lower()
```

Note: importing `route_fetch` from `tests.test_latest_videos` requires pytest's rootdir on `sys.path`; add an empty `tests/__init__.py` if the import fails when you run it.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL with `ImportError: cannot import name 'main'`.

- [ ] **Step 3: Implement the CLI**

Add to `youtube_latest.py` (new imports: `import argparse`, `import json`, `import sys`):

```python
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
```

- [ ] **Step 4: Run the full suite**

Run: `uv run pytest -v`
Expected: all 19 tests pass.

- [ ] **Step 5: Smoke-test against the real network (manual, not in CI)**

Run: `uv run python youtube_latest.py @mkbhd -n 3`
Expected: three real videos printed. If YouTube serves a consent wall in your region, the error path prints and exits 1 — the module still works where the page embeds the ID.

- [ ] **Step 6: Commit**

```bash
git add youtube_latest.py tests/test_cli.py
git commit -m "feat: CLI with human and JSON output"
```
