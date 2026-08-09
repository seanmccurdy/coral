from pathlib import Path

import youtube_latest
from youtube_latest import latest_videos

FIXTURES = Path(__file__).parent / "fixtures"
MKBHD_ID = "UCBJycsmduvYEL83R_U4JriQ"


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
    assert [r["channel"] for r in results] == ["@mkbhd", "@mkbhd", MKBHD_ID, MKBHD_ID]
    for r in results:
        assert r["channel_id"] == MKBHD_ID
        assert r["channel_title"] == "Marques Brownlee"
        assert "video_id" in r and "title" in r and "url" in r
        assert "published" in r and "thumbnail" in r and "views" in r
    # newest-first within each channel
    assert results[0]["video_id"] == "vid00000001"
    assert results[1]["video_id"] == "vid00000002"
    assert results[2]["video_id"] == "vid00000001"
    assert results[3]["video_id"] == "vid00000002"


def test_bare_name_normalized_in_result(monkeypatch):
    route_fetch(monkeypatch)
    assert latest_videos(["mkbhd"], n=1)[0]["channel"] == "@mkbhd"


def test_bad_handle_isolated_as_single_error_element(monkeypatch):
    route_fetch(monkeypatch)
    results = latest_videos(["@nosuchchannel", "@mkbhd"], n=1)
    error_elements = [r for r in results if r["channel"] == "@nosuchchannel"]
    assert len(error_elements) == 1
    assert "error" in error_elements[0]
    assert set(error_elements[0].keys()) == {"channel", "error"}
    other = [r for r in results if r["channel"] == "@mkbhd"]
    assert other[0]["channel_title"] == "Marques Brownlee"


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
