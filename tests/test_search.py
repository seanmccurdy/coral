import json
from datetime import datetime, timezone

import pytest

import youtube_search
from youtube_search import _parse_subscriber_count, main, search_videos

NOW = datetime(2026, 8, 9, tzinfo=timezone.utc)

CH_A = "UC" + "a" * 22
CH_B = "UC" + "b" * 22
CH_EXCLUDED = "UC" + "x" * 22


def renderer(video_id, title, channel_id, channel_name):
    return {
        "videoRenderer": {
            "videoId": video_id,
            "title": {"runs": [{"text": title}]},
            "ownerText": {
                "runs": [
                    {
                        "text": channel_name,
                        "navigationEndpoint": {"browseEndpoint": {"browseId": channel_id}},
                    }
                ]
            },
        }
    }


def player_response(published, views, description="desc"):
    resp = {
        "videoDetails": {
            "viewCount": str(views) if views is not None else None,
            "shortDescription": description,
            "thumbnail": {"thumbnails": [{"url": "https://i.ytimg.com/small"},
                                         {"url": "https://i.ytimg.com/big"}]},
        },
        "microformat": {"playerMicroformatRenderer": {}},
    }
    if published:
        resp["microformat"]["playerMicroformatRenderer"]["publishDate"] = published
    return resp


def channel_page(handle, subs_text):
    return (
        f'<html>{{"canonicalBaseUrl":"/{handle}"}}'
        f'... "{subs_text} subscribers" ...</html>'
    )


DEFAULT_SEARCH = {
    "vo2 max": [
        renderer("vidaaaaaaaa", "Norwegian 4x4", CH_A, "Dr A"),
        renderer("vidbbbbbbbb", "Zone 2 myths", CH_B, "Dr B"),
        renderer("vidxxxxxxxx", "From my own channel", CH_EXCLUDED, "Me"),
    ],
}

DEFAULT_META = {
    "vidaaaaaaaa": player_response("2026-07-20T07:00:10-07:00", 50000),
    "vidbbbbbbbb": player_response("2026-08-01T00:00:00+00:00", 900),
    "vidxxxxxxxx": player_response("2026-08-01T00:00:00+00:00", 10_000_000),
}

DEFAULT_CHANNELS = {
    CH_A: channel_page("@dra", "357K"),
    CH_B: channel_page("@drb", "800"),
}


def wire(monkeypatch, search=None, meta=None, channels=None, fail_queries=()):
    search = DEFAULT_SEARCH if search is None else search
    meta = DEFAULT_META if meta is None else meta
    channels = DEFAULT_CHANNELS if channels is None else channels

    def fake_post_json(url, payload):
        if url == youtube_search.SEARCH_URL:
            q = payload["query"]
            if q in fail_queries:
                raise OSError("search backend down")
            return {"contents": search.get(q, [])}
        vid = payload["videoId"]
        return meta[vid]

    def fake_fetch(url):
        cid = url.rsplit("/", 1)[1]
        if cid in channels:
            return channels[cid]
        raise OSError("channel page unavailable")

    monkeypatch.setattr(youtube_search, "_post_json", fake_post_json)
    monkeypatch.setattr(youtube_search, "_fetch", fake_fetch)
    monkeypatch.setattr(youtube_search, "_now", lambda: NOW)


def test_flat_mece_schema_with_query_key(monkeypatch):
    wire(monkeypatch)
    results = search_videos(["vo2 max"])
    assert len(results) == 3
    r = results[0]
    assert r == {
        "query": "vo2 max",
        "channel_handle": "@dra",
        "channel_id": CH_A,
        "channel_name": "Dr A",
        "channel_subscribers": 357_000,
        "video_id": "vidaaaaaaaa",
        "title": "Norwegian 4x4",
        "description": "desc",
        "url": "https://www.youtube.com/watch?v=vidaaaaaaaa",
        "published": datetime.fromisoformat("2026-07-20T07:00:10-07:00"),
        "thumbnail": "https://i.ytimg.com/big",
        "views": 50000,
    }


def test_dedupes_across_queries_first_query_wins(monkeypatch):
    wire(
        monkeypatch,
        search={
            "q1": [renderer("vidaaaaaaaa", "Norwegian 4x4", CH_A, "Dr A")],
            "q2": [renderer("vidaaaaaaaa", "Norwegian 4x4", CH_A, "Dr A")],
        },
    )
    results = search_videos(["q1", "q2"])
    assert len(results) == 1
    assert results[0]["query"] == "q1"


def test_excluded_channels_are_dropped(monkeypatch):
    wire(monkeypatch)
    results = search_videos(["vo2 max"], exclude_channels=[CH_EXCLUDED])
    assert [r["video_id"] for r in results] == ["vidaaaaaaaa", "vidbbbbbbbb"]


def test_days_window_uses_exact_dates(monkeypatch):
    wire(monkeypatch)
    results = search_videos(["vo2 max"], days=10)
    # vidaaaaaaaa published 2026-07-20, outside a 10-day window ending 2026-08-09
    assert "vidaaaaaaaa" not in [r["video_id"] for r in results]
    assert "vidbbbbbbbb" in [r["video_id"] for r in results]


def test_unknown_publish_date_fails_open(monkeypatch):
    wire(monkeypatch, meta={**DEFAULT_META, "vidaaaaaaaa": player_response(None, 50000)})
    results = search_videos(["vo2 max"], days=10)
    row = next(r for r in results if r["video_id"] == "vidaaaaaaaa")
    assert row["published"] is None


def test_min_views_filter(monkeypatch):
    wire(monkeypatch)
    results = search_videos(["vo2 max"], min_views=10_000)
    ids = [r["video_id"] for r in results]
    assert "vidbbbbbbbb" not in ids  # 900 views
    assert "vidaaaaaaaa" in ids


def test_min_subs_filter_and_subscriber_parsing(monkeypatch):
    wire(monkeypatch)
    results = search_videos(["vo2 max"], min_subs=100_000)
    ids = [r["video_id"] for r in results]
    assert "vidbbbbbbbb" not in ids  # 800 subs
    assert "vidaaaaaaaa" in ids  # 357K subs
    # channel with unavailable page: subscriber filter fails open
    row = next(r for r in results if r["channel_id"] == CH_EXCLUDED)
    assert row["channel_subscribers"] is None


@pytest.mark.parametrize(
    "text,expected",
    [
        ("357K", 357_000),
        ("1.23M", 1_230_000),
        ("18.9M", 18_900_000),
        ("1,234", 1_234),
        ("2B", 2_000_000_000),
        ("garbage subs", None),
    ],
)
def test_parse_subscriber_count(text, expected):
    assert _parse_subscriber_count(text) == expected


def test_failed_query_isolated_as_error(monkeypatch):
    wire(monkeypatch, fail_queries={"broken"})
    results = search_videos(["broken", "vo2 max"])
    assert results[0] == {"query": "broken", "error": "search backend down"}
    assert len([r for r in results if "error" not in r]) == 3


def test_transcripts_opt_in(monkeypatch):
    wire(monkeypatch)
    monkeypatch.setattr(
        youtube_search, "_fetch_transcript", lambda vid, use_cache=True: ("words", "en")
    )
    with_t = search_videos(["vo2 max"], include_transcripts=True)
    assert all(r["transcript"] == "words" for r in with_t)
    without = search_videos(["vo2 max"])
    assert "transcript" not in without[0]


def test_cli_json_and_flags(monkeypatch, capsys, tmp_path):
    wire(monkeypatch)
    qfile = tmp_path / "queries.txt"
    qfile.write_text("# topics\nvo2 max\n")
    code = main(["-q", str(qfile), "--min-views", "10000", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert [d["video_id"] for d in data] == ["vidaaaaaaaa", "vidxxxxxxxx"]


def test_cli_requires_queries(capsys):
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.code == 2
