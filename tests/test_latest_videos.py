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
