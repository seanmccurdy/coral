import pytest

import youtube_latest
import youtube_search


@pytest.fixture(autouse=True)
def clear_resolve_cache():
    youtube_latest.resolve_channel_id.cache_clear()
    yield
    youtube_latest.resolve_channel_id.cache_clear()


@pytest.fixture(autouse=True)
def isolated_transcript_cache(tmp_path, monkeypatch):
    """Keep tests away from the real on-disk caches."""
    monkeypatch.setattr(youtube_latest, "_CACHE_DIR", tmp_path / "transcripts")
    monkeypatch.setattr(youtube_latest, "_HANDLE_CACHE_DIR", tmp_path / "handles")
    monkeypatch.setattr(youtube_search, "_VIDEO_META_CACHE_DIR", tmp_path / "videometa")
    monkeypatch.setattr(youtube_search, "_CHANNEL_CACHE_DIR", tmp_path / "channels")
