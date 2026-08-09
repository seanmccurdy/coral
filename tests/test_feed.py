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
