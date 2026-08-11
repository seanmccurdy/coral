import json
from datetime import datetime, timezone

import pytest

import update_wiki
from update_wiki import (
    bootstrap_wiki,
    connect,
    integration_prompt,
    run_pipeline,
    unprocessed,
)


def video(vid, transcript="words " * 50, **over):
    v = {
        "video_id": vid,
        "channel_handle": "@chan",
        "channel_name": "Chan",
        "title": f"Video {vid}",
        "description": "desc",
        "url": f"https://www.youtube.com/watch?v={vid}",
        "published": datetime(2026, 8, 9, tzinfo=timezone.utc),
        "transcript": transcript,
        "transcript_language": "en",
    }
    v.update(over)
    return v


@pytest.fixture(autouse=True)
def isolated_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(update_wiki, "DB_PATH", tmp_path / "coral.db")
    monkeypatch.setattr(update_wiki, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(update_wiki, "WIKI_DIR", tmp_path / "wiki")


def fake_claude(monkeypatch, fail_on_batch=None, all_calls=None):
    calls = []  # claude invocations only; formatter calls go to all_calls

    def fake_run(cmd, **kwargs):
        if all_calls is not None:
            all_calls.append(cmd)
        if cmd[0] != "claude":

            class OK:
                returncode = 0

            return OK()
        calls.append(cmd)
        code = 1 if fail_on_batch is not None and len(calls) == fail_on_batch else 0

        class R:
            returncode = code

        return R()

    monkeypatch.setattr(update_wiki.subprocess, "run", fake_run)
    return calls


def test_unprocessed_filters_seen_and_transcriptless():
    conn = connect()
    videos = [video("aa"), video("bb", transcript=None), video("cc")]
    assert [v["video_id"] for v in unprocessed(conn, videos)] == ["aa", "cc"]
    fake = None  # mark "aa" processed, then only "cc" remains
    conn.execute(
        "INSERT INTO processed_videos (video_id, integrated_at) VALUES ('aa', 'now')"
    )
    assert [v["video_id"] for v in unprocessed(conn, videos)] == ["cc"]


def test_pipeline_stages_batches_and_marks_processed(monkeypatch):
    calls = fake_claude(monkeypatch)
    conn = connect()
    videos = [video(f"v{i}") for i in range(5)]
    summary = run_pipeline(videos, conn)
    # batches of 3: 5 videos -> 2 invocations, plus one synthesis pass
    assert len(calls) == 3
    assert summary["integrated"] == 5 and summary["failed_batches"] == 0
    assert summary["synthesis_ok"] is True
    assert unprocessed(conn, videos) == []
    # staging cleaned up after success
    assert list(update_wiki.STAGING_DIR.glob("*.md")) == []


def test_failed_batch_keeps_videos_unprocessed_and_staged(monkeypatch):
    fake_claude(monkeypatch, fail_on_batch=2)
    conn = connect()
    videos = [video(f"v{i}") for i in range(5)]
    summary = run_pipeline(videos, conn)
    assert summary["integrated"] == 3 and summary["failed_batches"] == 1
    remaining = unprocessed(conn, videos)
    assert [v["video_id"] for v in remaining] == ["v3", "v4"]
    # failed batch's staging files retained for inspection/retry
    staged = sorted(p.stem for p in update_wiki.STAGING_DIR.glob("*.md"))
    assert staged == ["v3", "v4"]


def test_staged_file_has_frontmatter_and_transcript(monkeypatch):
    fake_claude(monkeypatch)
    conn = connect()
    v = video("vv", transcript="the actual transcript text")
    staged_path = update_wiki.stage(v)
    text = staged_path.read_text()
    assert text.startswith("---\n")
    assert 'channel: "@chan (Chan)"' in text
    assert "url: https://www.youtube.com/watch?v=vv" in text
    assert "published: 2026-08-09" in text
    assert "the actual transcript text" in text


def test_prompt_names_staged_files_and_conventions():
    paths = ["staging/a.md", "staging/b.md"]
    prompt = integration_prompt(paths)
    for p in paths:
        assert p in prompt
    for needle in [
        "wiki/_index.md",
        "changelog.md",
        "[[",
        "frontmatter",
        "cite",
        "mermaid",
        "Gaps & open questions",
        "Practical implications",
        "contrarian",
    ]:
        assert needle in prompt


def test_synthesis_prompt_covers_model_and_playbook():
    for needle in [
        "aging-model.md",
        "practice-playbook.md",
        "mermaid",
        "postulat",
        "daily / weekly / monthly",
        "evidence-graded",
    ]:
        assert needle in update_wiki.SYNTHESIS_PROMPT


def test_no_formatter_invoked(monkeypatch):
    # Width is the reader's (Obsidian's) concern — the pipeline must never
    # rewrite md files to adjust wrapping.
    all_calls = []
    fake_claude(monkeypatch, all_calls=all_calls)
    conn = connect()
    run_pipeline([video("v1")], conn)
    assert all(c[0] == "claude" for c in all_calls)


def test_synthesis_skipped_when_nothing_integrated(monkeypatch):
    calls = fake_claude(monkeypatch, fail_on_batch=1)
    conn = connect()
    summary = run_pipeline([video("v1")], conn)
    assert summary["integrated"] == 0
    assert len(calls) == 1  # the failed batch only — no synthesis pass
    assert "synthesis_ok" not in summary


def test_dry_run_invokes_nothing_and_marks_nothing(monkeypatch):
    calls = fake_claude(monkeypatch)
    conn = connect()
    videos = [video("v1"), video("v2")]
    summary = run_pipeline(videos, conn, dry_run=True)
    assert calls == []
    assert summary["integrated"] == 0
    assert len(unprocessed(conn, videos)) == 2


def test_limit_caps_videos(monkeypatch):
    calls = fake_claude(monkeypatch)
    conn = connect()
    videos = [video(f"v{i}") for i in range(5)]
    summary = run_pipeline(videos, conn, limit=2)
    assert summary["integrated"] == 2
    assert len(calls) == 2  # one batch + one synthesis pass


def test_bootstrap_creates_index_and_changelog_once():
    bootstrap_wiki()
    index = update_wiki.WIKI_DIR / "_index.md"
    changelog = update_wiki.WIKI_DIR / "changelog.md"
    assert index.exists() and changelog.exists()
    marker = "# custom edit"
    index.write_text(index.read_text() + marker)
    bootstrap_wiki()  # idempotent: must not clobber
    assert marker in index.read_text()
