import json
from pathlib import Path

import youtube_latest
from youtube_latest import latest_videos

FIXTURES = Path(__file__).parent / "fixtures"
MKBHD_ID = "UCBJycsmduvYEL83R_U4JriQ"


def test_http_identity_is_not_explicitly_bot_labeled():
    assert "Mozilla/5.0" in youtube_latest._USER_AGENT
    assert "bot" not in youtube_latest._USER_AGENT.lower()


def route_fetch(monkeypatch, fail_feeds=(), no_uulf=(), empty_uulf=()):
    """_fetch stub: channel pages resolve via the HTML fixture, feeds via feed.xml.

    - fail_feeds: channel IDs for which the UC channel-feed fetch raises.
    - no_uulf: channel IDs for which the UULF playlist-feed fetch raises
      (forcing fallback to the UC channel feed).
    - empty_uulf: channel IDs for which the UULF playlist-feed parses but has
      zero videos (also forcing fallback).
    """
    page = (FIXTURES / "channel_page.html").read_text()
    feed = (FIXTURES / "feed.xml").read_text()
    playlist_feed = (FIXTURES / "playlist_feed.xml").read_text()
    empty_feed = (FIXTURES / "empty_feed.xml").read_text()

    def fake_fetch(url):
        if "playlist_id=UULF" in url:
            cid = url.split("playlist_id=UULF")[1]
            cid = "UC" + cid
            if cid in no_uulf:
                raise OSError("connection reset")
            if cid in empty_uulf:
                return empty_feed
            return playlist_feed
        if "feeds/videos.xml" in url and "channel_id=" in url:
            cid = url.split("channel_id=")[1]
            if cid in fail_feeds:
                raise OSError("connection reset")
            return feed
        if url == "https://www.youtube.com/@nosuchchannel":
            return "<html>no id here</html>"
        return page

    monkeypatch.setattr(youtube_latest, "_fetch", fake_fetch)


def test_returns_flat_list_of_videos_in_channel_then_recency_order(monkeypatch):
    route_fetch(monkeypatch)
    results = latest_videos(["@mkbhd", MKBHD_ID], n=2)
    # playlist_feed.xml has 2 videos per channel -> 2 channels * 2 videos = 4 elements
    assert len(results) == 4
    assert [r["channel_handle"] for r in results] == ["@mkbhd", "@mkbhd", MKBHD_ID, MKBHD_ID]
    for r in results:
        assert r["channel_id"] == MKBHD_ID
        assert r["channel_name"] == "Marques Brownlee"
        assert set(r.keys()) == {
            "channel_handle", "channel_id", "channel_name",
            "video_id", "title", "description", "url",
            "published", "thumbnail", "views",
        }
    # newest-first within each channel
    assert results[0]["video_id"] == "vid00000001"
    assert results[1]["video_id"] == "vid00000002"
    assert results[2]["video_id"] == "vid00000001"
    assert results[3]["video_id"] == "vid00000002"


def test_bare_name_normalized_in_result(monkeypatch):
    route_fetch(monkeypatch)
    assert latest_videos(["mkbhd"], n=1)[0]["channel_handle"] == "@mkbhd"


def test_bad_handle_isolated_as_single_error_element(monkeypatch):
    route_fetch(monkeypatch)
    results = latest_videos(["@nosuchchannel", "@mkbhd"], n=1)
    error_elements = [r for r in results if r["channel_handle"] == "@nosuchchannel"]
    assert len(error_elements) == 1
    assert "error" in error_elements[0]
    assert set(error_elements[0].keys()) == {"channel_handle", "error"}
    other = [r for r in results if r["channel_handle"] == "@mkbhd"]
    assert other[0]["channel_name"] == "Marques Brownlee"


def test_feed_fetch_failure_isolated_as_error(monkeypatch):
    # Both the UULF fetch and the fallback UC feed fetch fail.
    route_fetch(monkeypatch, fail_feeds={MKBHD_ID}, no_uulf={MKBHD_ID})
    results = latest_videos(["@mkbhd"], n=1)
    assert len(results) == 1
    assert results[0]["error"] == "connection reset"


def test_n_is_clamped(monkeypatch):
    route_fetch(monkeypatch)
    assert len(latest_videos(["@mkbhd"], n=99)[0:2]) == 2  # fixture has 2 per channel
    assert len(latest_videos(["@mkbhd"], n=0)) == 1


def test_empty_channel_list(monkeypatch):
    route_fetch(monkeypatch)
    assert latest_videos([]) == []


def test_uulf_feed_used_when_available(monkeypatch):
    route_fetch(monkeypatch)
    results = latest_videos(["@mkbhd"], n=2)
    titles = [r["title"] for r in results]
    assert titles == ["Newest Long-Form Video", "Older Long-Form Video"]


def test_falls_back_to_channel_feed_when_uulf_fetch_raises(monkeypatch):
    route_fetch(monkeypatch, no_uulf={MKBHD_ID})
    results = latest_videos(["@mkbhd"], n=3)
    titles = [r["title"] for r in results]
    assert titles == ["Newest Video", "Middle Video", "Oldest Video"]


def test_falls_back_to_channel_feed_when_uulf_has_zero_videos(monkeypatch):
    route_fetch(monkeypatch, empty_uulf={MKBHD_ID})
    results = latest_videos(["@mkbhd"], n=3)
    titles = [r["title"] for r in results]
    assert titles == ["Newest Video", "Middle Video", "Oldest Video"]


def test_include_shorts_skips_uulf_and_uses_mixed_channel_feed(monkeypatch):
    calls = []
    page = (FIXTURES / "channel_page.html").read_text()
    feed = (FIXTURES / "feed.xml").read_text()

    def fake_fetch(url):
        calls.append(url)
        if "feeds/videos.xml" in url and "channel_id=" in url:
            return feed
        return page

    monkeypatch.setattr(youtube_latest, "_fetch", fake_fetch)
    results = latest_videos(["@mkbhd"], n=3, include_shorts=True)
    titles = [r["title"] for r in results]
    assert titles == ["Newest Video", "Middle Video", "Oldest Video"]
    assert not any("playlist_id=UULF" in u for u in calls)


def test_http_feed_failure_uses_ytdlp_fallback(monkeypatch):
    page = (FIXTURES / "channel_page.html").read_text()

    def fake_fetch(url):
        if "feeds/videos.xml" in url:
            raise youtube_latest.urllib.error.HTTPError(url, 404, "gone", {}, None)
        return page

    class Result:
        returncode = 0
        stderr = ""
        stdout = json.dumps(
            {
                "id": "fallback001",
                "title": "Fallback video",
                "description": "description",
                "webpage_url": "https://www.youtube.com/watch?v=fallback001",
                "upload_date": "20260810",
                "thumbnail": "thumb.jpg",
                "view_count": 123,
                "channel": "Fallback Channel",
            }
        )

    monkeypatch.setattr(youtube_latest, "_fetch", fake_fetch)
    monkeypatch.setattr(youtube_latest.subprocess, "run", lambda *a, **k: Result())
    result = latest_videos(["@mkbhd"], n=1)[0]
    assert result["video_id"] == "fallback001"
    assert result["channel_name"] == "Fallback Channel"
    assert result["published"].date().isoformat() == "2026-08-10"
