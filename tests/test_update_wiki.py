import json
from datetime import date, datetime, timezone

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
    last_claude_failed = False

    def fake_run(cmd, **kwargs):
        nonlocal last_claude_failed
        if all_calls is not None:
            all_calls.append(cmd)
        if cmd[0] == "codex":

            class CodexResult:
                returncode = 1 if last_claude_failed else 0

            return CodexResult()
        if cmd[0] != "claude":

            class OK:
                returncode = 0

            return OK()
        calls.append(cmd)
        code = 1 if fail_on_batch is not None and len(calls) == fail_on_batch else 0
        last_claude_failed = code != 0

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
    assert "## Video description\n\ndesc" in text
    assert "## Transcript" in text
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
        "textbook",
        "TEACHES",
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


def test_refresh_prompt_enforces_textbook_refactor():
    for needle in [
        "every Markdown page",
        "first principles",
        "podcast-summary narration",
        "larger system",
        "evidence",
        "Practical implications",
        "Gaps & open questions",
        "one paragraph per line",
        "use only claims and sources already present",
        "changelog.md",
    ]:
        assert needle in update_wiki.REFRESH_PROMPT


def test_refresh_wiki_bootstraps_and_invokes_claude_once(monkeypatch):
    calls = fake_claude(monkeypatch)
    assert update_wiki.refresh_wiki() is True
    assert (update_wiki.WIKI_DIR / "_index.md").exists()
    assert len(calls) == 1
    assert update_wiki.REFRESH_PROMPT in calls[0]


def test_refresh_cli_skips_video_retrieval(monkeypatch):
    calls = fake_claude(monkeypatch)

    def unexpected_collect(*args, **kwargs):
        raise AssertionError("refresh must not retrieve videos")

    monkeypatch.setattr(update_wiki, "collect_videos", unexpected_collect)
    assert update_wiki.main(["--refresh-wiki"]) == 0
    assert len(calls) == 1


def test_enrichment_prompt_requires_primary_evidence_and_reference_integrity():
    prompt = update_wiki.enrichment_prompt(2)
    for needle in [
        "first 2",
        "Clinical guidelines",
        "Randomized controlled trials",
        "primary or authoritative sources",
        "## References",
        "every use has a definition",
        "episode citations as provenance",
        "Do not modify anything outside wiki/",
    ]:
        assert needle in prompt


def test_enrich_cli_skips_video_retrieval_and_enables_web(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)

        class Result:
            returncode = 0

        return Result()

    def unexpected_collect(*args, **kwargs):
        raise AssertionError("enrichment must not retrieve videos")

    monkeypatch.setattr(update_wiki.subprocess, "run", fake_run)
    monkeypatch.setattr(update_wiki, "collect_videos", unexpected_collect)
    assert update_wiki.main(["--enrich-wiki", "--pages", "2", "--engine", "codex"]) == 0
    assert len(calls) == 1
    assert calls[0][0] == "codex"
    assert calls[0].index("--search") < calls[0].index("exec")
    assert update_wiki.enrichment_prompt(2) in calls[0]


def test_reference_validator_accepts_valid_and_reports_structural_errors():
    concept_dir = update_wiki.WIKI_DIR / "concepts"
    concept_dir.mkdir(parents=True)
    good = concept_dir / "good.md"
    good.write_text(
        "Claim.[^trial]\n\n## References\n\n"
        "[^trial]: Authors. Title. Journal (2024). [RCT]. [DOI](https://doi.org/10/x)\n"
    )
    assert update_wiki.validate_wiki_references() == []

    bad = concept_dir / "bad.md"
    bad.write_text(
        "Unsupported use.[^missing]\n\n## References\n\n"
        "[^unused]: Authors. Title. Journal (2024). no link\n"
    )
    errors = update_wiki.validate_wiki_references()
    assert any("[^missing] has no definition" in error for error in errors)
    assert any("[^unused] is defined but unused" in error for error in errors)
    assert any("[^unused] lacks a linked source" in error for error in errors)
    assert any("[^unused] lacks an evidence-type label" in error for error in errors)


def test_link_validator_supports_nested_concepts_and_reports_missing_targets():
    nested = update_wiki.WIKI_DIR / "concepts" / "aging-biology"
    nested.mkdir(parents=True)
    (nested / "known.md").write_text("# Known\n")
    source = update_wiki.WIKI_DIR / "synthesis" / "model.md"
    source.parent.mkdir(parents=True)
    source.write_text("See [[known]] and [[missing]].\n")
    errors = update_wiki.validate_wiki_links()
    assert not any("known" in error for error in errors)
    assert any("unresolved [[missing]]" in error for error in errors)


def test_freshness_report_marks_overdue_and_missing_metadata():
    concept_dir = update_wiki.WIKI_DIR / "concepts"
    concept_dir.mkdir(parents=True)
    (concept_dir / "old.md").write_text(
        "---\ntype: concept\ntitle: Old\ntags: [longevity]\nupdated: 2025-01-01\n"
        "evidence_reviewed: 2025-01-01\nevidence_cutoff: 2025-01-01\n"
        "review_status: current\nreview_interval: 30d\n---\n"
    )
    (concept_dir / "missing.md").write_text("---\ntype: concept\n---\n")
    report, errors = update_wiki.freshness_report(date(2026, 1, 1))
    assert "concepts/old.md` | 2025-01-31 | review-due" in report
    assert any("concepts/missing.md: incomplete" in error for error in errors)


def test_freshness_report_accepts_never_reviewed_baseline():
    concept_dir = update_wiki.WIKI_DIR / "concepts"
    concept_dir.mkdir(parents=True)
    (concept_dir / "legacy.md").write_text(
        "---\ntype: concept\ntitle: Legacy\ntags: [longevity]\nupdated: 2026-01-01\n"
        "evidence_reviewed: never\nevidence_cutoff: unknown\n"
        "review_status: review-due\nreview_interval: 365d\n---\n"
    )
    report, errors = update_wiki.freshness_report(date(2026, 1, 1))
    assert errors == []
    assert "concepts/legacy.md` | now | review-due" in report


def test_audit_prompt_requires_corrections_and_synthesis_reconciliation():
    for needle in [
        "superseded, contradicted, retracted",
        "Evidence update",
        "Never silently overwrite",
        "Reconcile every synthesis page",
        "synthesis-impact report",
    ]:
        assert needle in update_wiki.AUDIT_PROMPT


def test_transaction_restores_wiki_when_agent_leaves_invalid_edit(monkeypatch):
    update_wiki.bootstrap_wiki()
    index = update_wiki.WIKI_DIR / "_index.md"
    original = index.read_text()

    def corrupt(*args, **kwargs):
        index.write_text(original + "\n[[definitely-missing]]\n")
        return True

    monkeypatch.setattr(update_wiki, "run_agent", corrupt)
    assert update_wiki.run_agent_transactional("edit") is False
    assert index.read_text() == original


def test_hypothesis_transaction_rejects_successful_noop(monkeypatch):
    update_wiki.bootstrap_wiki()
    monkeypatch.setattr(update_wiki, "run_agent", lambda *args, **kwargs: True)
    assert update_wiki.run_agent_transactional("ideate", require_changes=True) is False


def test_schema_validator_rejects_concept_in_root():
    update_wiki.bootstrap_wiki()
    path = update_wiki.WIKI_DIR / "concepts" / "wrong.md"
    path.write_text("# wrong\n")
    assert any("concepts root" in error for error in update_wiki.validate_wiki_schema())


def test_schema_validator_requires_hypothesis_test_contract():
    update_wiki.bootstrap_wiki()
    hypotheses = update_wiki.WIKI_DIR / "hypotheses"
    hypotheses.mkdir()
    (hypotheses / "idea.md").write_text(
        "---\ntype: hypothesis\ntitle: Idea\ntags: [longevity]\nupdated: 2026-08-12\n"
        "evidence_reviewed: never\nevidence_cutoff: unknown\nreview_status: review-due\n"
        "review_interval: 90d\n---\n\n# Idea\n"
    )
    errors = update_wiki.validate_wiki_schema()
    assert any("hypotheses/idea.md: missing frontmatter hypothesis_status" in error for error in errors)
    assert any("hypotheses/idea.md: missing ## Mechanistic model" in error for error in errors)
    assert any("hypotheses/idea.md: missing ## Testable predictions" in error for error in errors)


def test_hypothesis_prompt_is_bounded_falsifiable_and_safe():
    prompt = update_wiki.hypothesis_prompt(1)
    for needle in [
        "no more than 1 new hypothesis", "create none", "falsifiable",
        "strongest alternative explanation", "safest decisive test",
        "revise, or retire", "Do not turn a hypothesis into personal advice",
        "synthesis-impact check", "exactly three distinct", "no more than twelve active seeds",
        "strongest candidate", "Mermaid mechanistic model", "major harm branch",
        "Scope is human-direct", "without a wet lab", "Biomarkers and device metrics",
        "PubMed-indexed human studies", "Podcast and video material",
        "Run only the evidence-review stage", "eight external sources",
    ]:
        assert needle in prompt


def test_hypothesis_ideation_prompt_requires_three_seeds_and_no_research():
    prompt = update_wiki.hypothesis_ideation_prompt()
    assert "exactly three distinct" in prompt
    assert "Do not research or promote" in prompt
    assert "no nursery change is a failure" in prompt


def test_hypothesis_dry_run_does_not_invoke_agent(monkeypatch, capsys):
    monkeypatch.setattr(update_wiki, "run_agent_transactional", lambda *args, **kwargs: pytest.fail("agent invoked"))
    assert update_wiki.develop_hypotheses(1, dry_run=True) is True
    assert "weekly Coral hypothesis workshop" in capsys.readouterr().out


def test_dependency_graph_identifies_synthesis_consumers():
    concept = update_wiki.WIKI_DIR / "concepts" / "aging-biology"
    concept.mkdir(parents=True)
    (concept / "topic.md").write_text("# Topic\n")
    synthesis = update_wiki.WIKI_DIR / "synthesis"
    synthesis.mkdir(parents=True)
    (synthesis / "model.md").write_text("See [[topic]].\n")
    graph = update_wiki.build_dependency_graph()
    assert graph["topic"]["synthesis"] == ["model"]


def test_source_registry_deduplicates_sources_across_pages():
    concept = update_wiki.WIKI_DIR / "concepts" / "aging-biology"
    concept.mkdir(parents=True)
    reference = "[^x]: Authors. Title. [RCT]. [DOI](https://doi.org/10.1000/Test)\n"
    (concept / "one.md").write_text("Claim.[^x]\n\n## References\n" + reference)
    (concept / "two.md").write_text("Claim.[^x]\n\n## References\n" + reference)
    registry = update_wiki.build_source_registry()
    assert list(registry) == ["doi:10.1000/test"]
    assert registry["doi:10.1000/test"]["pages"] == [
        "concepts/aging-biology/one.md", "concepts/aging-biology/two.md"
    ]


def test_cli_passes_per_channel_depth(monkeypatch):
    captured = {}

    def fake_collect(channels, queries, videos_per_channel=15):
        captured["videos_per_channel"] = videos_per_channel
        return []

    monkeypatch.setattr(update_wiki, "collect_videos", fake_collect)
    assert update_wiki.main(["--channels-only", "--videos-per-channel", "3"]) == 0
    assert captured["videos_per_channel"] == 3


def test_auto_engine_falls_back_to_codex(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)

        class Result:
            returncode = 1 if cmd[0] == "claude" else 0

        return Result()

    monkeypatch.setattr(update_wiki.subprocess, "run", fake_run)
    assert update_wiki.run_agent("edit the wiki") is True
    assert [cmd[0] for cmd in calls] == ["claude", "codex"]
    assert calls[1][1:4] == ["--ask-for-approval", "never", "exec"]
    assert "workspace-write" in calls[1]


def test_explicit_codex_engine_skips_claude(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(update_wiki.subprocess, "run", fake_run)
    assert update_wiki.run_agent("edit the wiki", "codex") is True
    assert len(calls) == 1 and calls[0][0] == "codex"


def test_no_formatter_invoked(monkeypatch):
    # Width is the reader's (Obsidian's) concern — the pipeline must never
    # rewrite md files to adjust wrapping.
    all_calls = []
    fake_claude(monkeypatch, all_calls=all_calls)
    conn = connect()
    run_pipeline([video("v1")], conn)
    assert all(c[0] in ("claude", "codex") for c in all_calls)


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
    queue = update_wiki.WIKI_DIR / "_research-queue.md"
    assert index.exists() and changelog.exists() and queue.exists()
    assert "Cellular senescence" in queue.read_text()
    marker = "# custom edit"
    index.write_text(index.read_text() + marker)
    queue_marker = "\n- [ ] P2 custom research question\n"
    queue.write_text(queue.read_text() + queue_marker)
    bootstrap_wiki()  # idempotent: must not clobber
    assert marker in index.read_text()
    assert queue_marker in queue.read_text()
