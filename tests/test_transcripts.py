import time

import youtube_latest
from youtube_latest import _fetch_transcript, latest_videos

from tests.test_latest_videos import route_fetch

TIMEDTEXT_XML = (
    '<?xml version="1.0" encoding="utf-8" ?><timedtext format="3">\n'
    '<head><ws id="0"/></head>\n'
    '<body>'
    '<p t="0" d="2000">Hello world</p>'
    '<p t="2000" d="1500"><s>this </s><s>is</s> a test</p>'
    '<p t="4000" d="100"> </p>'
    "</body></timedtext>"
)


def player_response(tracks):
    return {"captions": {"playerCaptionsTracklistRenderer": {"captionTracks": tracks}}}


def mock_transcript_seams(monkeypatch, response, caption_xml=TIMEDTEXT_XML):
    posts = []
    fetched = []

    def fake_post_json(url, payload):
        posts.append((url, payload))
        if isinstance(response, Exception):
            raise response
        return response

    def fake_fetch(url):
        fetched.append(url)
        return caption_xml

    monkeypatch.setattr(youtube_latest, "_post_json", fake_post_json)
    monkeypatch.setattr(youtube_latest, "_fetch", fake_fetch)
    return posts, fetched


def test_transcript_text_is_joined_from_timedtext(monkeypatch):
    mock_transcript_seams(
        monkeypatch,
        player_response([{"baseUrl": "https://captions.example/en", "languageCode": "en"}]),
    )
    text, lang = _fetch_transcript("vid00000001")
    assert text == "Hello world this is a test"
    assert lang == "en"


def test_manual_track_preferred_over_auto_generated(monkeypatch):
    _, fetched = mock_transcript_seams(
        monkeypatch,
        player_response(
            [
                {"baseUrl": "https://captions.example/asr", "languageCode": "en", "kind": "asr"},
                {"baseUrl": "https://captions.example/manual", "languageCode": "en"},
            ]
        ),
    )
    _fetch_transcript("vid00000001")
    assert fetched == ["https://captions.example/manual"]


def test_no_caption_tracks_gives_none(monkeypatch):
    mock_transcript_seams(monkeypatch, player_response([]))
    assert _fetch_transcript("vid00000001") == (None, None)


def test_player_error_gives_none(monkeypatch):
    mock_transcript_seams(monkeypatch, OSError("connection reset"))
    assert _fetch_transcript("vid00000001") == (None, None)


def test_latest_videos_adds_transcript_fields_when_enabled(monkeypatch):
    route_fetch(monkeypatch)
    feed_fetch = youtube_latest._fetch  # route_fetch's stub for pages/feeds

    def fetch_with_captions(url):
        if url.startswith("https://captions.example/"):
            return TIMEDTEXT_XML
        return feed_fetch(url)

    monkeypatch.setattr(youtube_latest, "_fetch", fetch_with_captions)
    monkeypatch.setattr(
        youtube_latest,
        "_post_json",
        lambda url, payload: player_response(
            [{"baseUrl": "https://captions.example/en", "languageCode": "en"}]
        ),
    )
    results = latest_videos(["@mkbhd"], n=2, include_transcripts=True)
    assert all(r["transcript"] == "Hello world this is a test" for r in results)
    assert all(r["transcript_language"] == "en" for r in results)


def test_latest_videos_omits_transcript_fields_by_default(monkeypatch):
    route_fetch(monkeypatch)
    results = latest_videos(["@mkbhd"], n=1)
    assert "transcript" not in results[0]
    assert "transcript_language" not in results[0]


def test_transcript_is_cached_on_disk_and_reused(monkeypatch):
    posts, fetched = mock_transcript_seams(
        monkeypatch,
        player_response([{"baseUrl": "https://captions.example/en", "languageCode": "en"}]),
    )
    first = _fetch_transcript("vid00000001")
    assert first == ("Hello world this is a test", "en")
    assert len(posts) == 1 and len(fetched) == 1

    second = _fetch_transcript("vid00000001")
    assert second == first
    # no additional network traffic: served from the disk cache
    assert len(posts) == 1 and len(fetched) == 1


def test_use_cache_false_bypasses_cache(monkeypatch):
    posts, fetched = mock_transcript_seams(
        monkeypatch,
        player_response([{"baseUrl": "https://captions.example/en", "languageCode": "en"}]),
    )
    _fetch_transcript("vid00000001", use_cache=False)
    _fetch_transcript("vid00000001", use_cache=False)
    assert len(posts) == 2 and len(fetched) == 2


def test_default_retention_is_about_one_year():
    assert youtube_latest._CACHE_TTL_SECONDS == 365 * 24 * 60 * 60


def test_expired_entries_are_refetched(monkeypatch):
    posts, _ = mock_transcript_seams(
        monkeypatch,
        player_response([{"baseUrl": "https://captions.example/en", "languageCode": "en"}]),
    )
    monkeypatch.setattr(youtube_latest, "_CACHE_TTL_SECONDS", 0.05)
    _fetch_transcript("vid00000001")
    time.sleep(0.1)
    _fetch_transcript("vid00000001")
    # entry expired between calls, so the second call hit the network again
    assert len(posts) == 2


def test_missing_transcript_is_not_cached(monkeypatch):
    posts, _ = mock_transcript_seams(monkeypatch, player_response([]))
    assert _fetch_transcript("vid00000001") == (None, None)
    assert _fetch_transcript("vid00000001") == (None, None)
    # captions can appear later (e.g. ASR still processing), so None is retried
    assert len(posts) == 2


def test_latest_videos_passes_use_cache_through(monkeypatch):
    route_fetch(monkeypatch)
    feed_fetch = youtube_latest._fetch
    caption_fetches = []

    def fetch_with_captions(url):
        if url.startswith("https://captions.example/"):
            caption_fetches.append(url)
            return TIMEDTEXT_XML
        return feed_fetch(url)

    monkeypatch.setattr(youtube_latest, "_fetch", fetch_with_captions)
    monkeypatch.setattr(
        youtube_latest,
        "_post_json",
        lambda url, payload: player_response(
            [{"baseUrl": "https://captions.example/en", "languageCode": "en"}]
        ),
    )
    latest_videos(["@mkbhd"], n=1, include_transcripts=True)
    latest_videos(["@mkbhd"], n=1, include_transcripts=True)
    assert len(caption_fetches) == 1  # second run served from cache

    latest_videos(["@mkbhd"], n=1, include_transcripts=True, use_cache=False)
    assert len(caption_fetches) == 2
