import pytest

import youtube_latest


@pytest.fixture(autouse=True)
def clear_resolve_cache():
    youtube_latest.resolve_channel_id.cache_clear()
    yield
    youtube_latest.resolve_channel_id.cache_clear()


@pytest.fixture(autouse=True)
def isolated_transcript_cache(tmp_path, monkeypatch):
    """Keep tests away from the real on-disk transcript cache."""
    monkeypatch.setattr(youtube_latest, "_CACHE_DIR", tmp_path / "transcripts")
