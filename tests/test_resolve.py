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


def test_resolution_survives_process_cache_clear_via_disk(monkeypatch):
    calls = mock_fetch(monkeypatch, body=(FIXTURES / "channel_page.html").read_text())
    assert resolve_channel_id("@mkbhd") == MKBHD_ID
    assert len(calls) == 1
    # simulate a fresh process: in-memory cache gone, network now failing
    resolve_channel_id.cache_clear()
    mock_fetch(monkeypatch, exc=OSError("network down"))
    assert resolve_channel_id("@mkbhd") == MKBHD_ID  # served from disk


def test_resolution_is_cached(monkeypatch):
    calls = mock_fetch(monkeypatch, body=(FIXTURES / "channel_page.html").read_text())
    resolve_channel_id("@mkbhd")
    resolve_channel_id("@mkbhd")
    assert len(calls) == 1


def test_handle_and_bare_name_share_one_cache_entry(monkeypatch):
    calls = mock_fetch(monkeypatch, body=(FIXTURES / "channel_page.html").read_text())
    assert resolve_channel_id("@mkbhd") == MKBHD_ID
    assert resolve_channel_id("mkbhd") == MKBHD_ID
    assert len(calls) == 1


def test_resolves_from_canonical_url_without_channel_id_key(monkeypatch):
    body = (
        "<html><head>"
        '<meta property="og:url" content="https://www.youtube.com/channel/'
        f'{MKBHD_ID}">'
        '<link rel="canonical" href="https://www.youtube.com/channel/'
        f'{MKBHD_ID}">'
        "</head><body></body></html>"
    )
    assert '"channelId"' not in body
    calls = mock_fetch(monkeypatch, body=body)
    assert resolve_channel_id("@mkbhd") == MKBHD_ID
    assert calls == ["https://www.youtube.com/@mkbhd"]


def test_canonical_link_wins_over_unrelated_channel_id(monkeypatch):
    # Real pages often contain an unrelated/related channel's "channelId" key
    # BEFORE the canonical link for the actual channel being viewed. The
    # canonical/og:url channel URL must take priority over any bare
    # "channelId" occurrence.
    wrong_id = "UCzzzzzzzzzzzzzzzzzzzzzz"
    body = (
        "<html><head>"
        f'<script>{{"channelId":"{wrong_id}"}}</script>'
        '<link rel="canonical" href="https://www.youtube.com/channel/'
        f'{MKBHD_ID}">'
        "</head><body></body></html>"
    )
    calls = mock_fetch(monkeypatch, body=body)
    assert resolve_channel_id("@mkbhd") == MKBHD_ID
    assert calls == ["https://www.youtube.com/@mkbhd"]
