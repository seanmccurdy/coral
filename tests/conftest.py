import pytest

import youtube_latest


@pytest.fixture(autouse=True)
def clear_resolve_cache():
    youtube_latest.resolve_channel_id.cache_clear()
    yield
    youtube_latest.resolve_channel_id.cache_clear()
