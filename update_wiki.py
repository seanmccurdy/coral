"""Integrate new video transcripts into the coral knowledge wiki.

Retrieves new videos (channel pulls + query search), diffs against the
seen-state store, and feeds transcripts in small batches to headless
Claude Code (`claude -p`), which updates the OKF-style wiki in wiki/.
Videos are marked processed only after their batch integrates successfully.
"""
from __future__ import annotations

import argparse
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from youtube_latest import latest_videos_from_file
from youtube_search import search_videos
from youtube_latest import _read_channels_file

DB_PATH = Path("coral.db")
STAGING_DIR = Path("staging")
WIKI_DIR = Path("wiki")
BATCH_SIZE = 3
CLAUDE_ALLOWED_TOOLS = "Read,Glob,Grep,Write,Edit"

_INDEX_TEMPLATE = """\
# Coral Wiki

A living knowledge base built from video transcripts. Organized by entity
type; domains (longevity, nutrition, fitness, hormones, sleep-brain,
skincare, urbanism) live in each page's `tags` frontmatter.

## Sections

- `concepts/` — mechanisms & ideas (e.g. vo2-max, autophagy)
- `interventions/` — things you can do or take (e.g. rapamycin, creatine, hrt)
- `people/` — researchers & recurring voices (e.g. peter-attia)
- `debates/` — live disagreements (e.g. seed-oils)
- `synthesis/` — big-picture pages maintained across all videos:
  - `aging-model.md` — the grand causal map: how aging mechanisms connect
    (mermaid diagrams), which interventions act on which nodes, clearly
    labeled postulations about causality
  - `practice-playbook.md` — what to actually do daily / weekly / monthly /
    periodically, evidence-graded, linking to the pages that justify each

## Page conventions

- Frontmatter: `type` (concept | intervention | person | debate |
  synthesis), `title`, `tags` (domains), `updated` (YYYY-MM-DD).
- Link related pages with [[wikilinks]] (the target file's stem); keep a
  "Related" section of links at the bottom of each page.
- Every claim cites its source inline:
  (Channel — "Video Title", YYYY-MM-DD, [link](url)).
- **Diagrams**: when a mechanism, pathway, or system has structure (causal
  chains, feedback loops, decision flows), draw it as a ```mermaid block
  (flowchart or graph) rather than describing it only in prose.
- **Gaps & open questions**: each substantive page keeps a section for
  what is unknown, unmeasured, or understudied — distinct from debates
  (contested claims); a gap is a question nobody has answered yet.
- **Practical implications**: each concept/intervention page states what a
  person should actually do with this knowledge (and at what cadence),
  with the strength of evidence behind it.
- **Unique perspectives**: contrarian or minority takes are captured and
  attributed to their proponent, not averaged into consensus.
- Conflicting claims are recorded as disagreements (prefer a debates/
  page), never silently overwritten.
- Formatting: prose is wrapped at 80 columns. Don't fight this — a
  formatter pass (mdformat) normalizes it after every run.

## Notable pages

(maintained by the integration agent as pages are added)
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS processed_videos (
               video_id TEXT PRIMARY KEY,
               channel_handle TEXT,
               title TEXT,
               published TEXT,
               integrated_at TEXT
           )"""
    )
    conn.commit()
    return conn


def unprocessed(conn: sqlite3.Connection, videos: list[dict]) -> list[dict]:
    """Videos not yet integrated, that actually have a transcript (a video
    whose transcript isn't available yet is retried on a later run)."""
    seen = {row[0] for row in conn.execute("SELECT video_id FROM processed_videos")}
    return [v for v in videos if v["video_id"] not in seen and v.get("transcript")]


def mark_processed(conn: sqlite3.Connection, videos: list[dict]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.executemany(
        "INSERT OR REPLACE INTO processed_videos VALUES (?, ?, ?, ?, ?)",
        [
            (
                v["video_id"],
                v.get("channel_handle"),
                v.get("title"),
                str(v.get("published") or ""),
                now,
            )
            for v in videos
        ],
    )
    conn.commit()


def bootstrap_wiki() -> None:
    """Create the wiki skeleton if absent; never clobber existing files."""
    for sub in ("concepts", "interventions", "people", "debates", "synthesis"):
        (WIKI_DIR / sub).mkdir(parents=True, exist_ok=True)
    index = WIKI_DIR / "_index.md"
    if not index.exists():
        index.write_text(_INDEX_TEMPLATE)
    changelog = WIKI_DIR / "changelog.md"
    if not changelog.exists():
        changelog.write_text("# Changelog\n")


def stage(video: dict) -> Path:
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    published = video.get("published")
    date = published.date().isoformat() if published else "?"
    path = STAGING_DIR / f"{video['video_id']}.md"
    path.write_text(
        "---\n"
        f'channel: "{video.get("channel_handle")} ({video.get("channel_name")})"\n'
        f'title: "{(video.get("title") or "").replace(chr(34), chr(39))}"\n'
        f"published: {date}\n"
        f"url: {video['url']}\n"
        f"views: {video.get('views')}\n"
        "---\n\n"
        f"{video.get('transcript') or ''}\n"
    )
    return path


def integration_prompt(staged_paths: list[str]) -> str:
    files = "\n".join(f"- {p}" for p in staged_paths)
    return f"""You maintain the coral knowledge wiki in wiki/ (an OKF-style bundle of
markdown concept pages). Read wiki/_index.md first — it defines the
sections and page conventions.

Integrate the following new video transcripts into the wiki:

{files}

Each staged file has frontmatter (channel, title, published date, url) and
the full transcript. For each video:

1. Identify the substantive claims, protocols, findings, positions — and
   the genuinely unique or contrarian perspectives, attributed to their
   proponents.
2. Update the relevant existing pages under wiki/concepts/,
   wiki/interventions/, wiki/people/, wiki/debates/ — or create new pages
   where a topic has none. Follow the frontmatter and page conventions
   from wiki/_index.md exactly, including per page:
   - a ```mermaid diagram wherever a mechanism, pathway, feedback loop,
     or decision flow has structure worth seeing (not decoration —
     draw the actual causal/decision structure discussed)
   - a "Gaps & open questions" section (what's unknown or unmeasured)
   - a "Practical implications" section (what to do, at what cadence,
     with the strength of evidence)
3. Integrate, don't append: merge new information into the page's existing
   structure where it belongs. Every claim you add must cite its source
   inline as (Channel — "Video Title", YYYY-MM-DD, [link](url)) using the
   staged file's frontmatter.
4. When a new claim conflicts with something already on a page, record the
   disagreement explicitly (move contested points to a debates/ page if
   substantial) — never silently overwrite or drop either side.
5. Maintain [[wikilinks]] between related pages and each page's Related
   section. Update wiki/_index.md's Notable pages list if you add pages.
6. Append one entry to wiki/changelog.md under today's date: each video on
   one line with the pages it created/updated.

Work through every staged file. Do not modify anything outside wiki/."""


SYNTHESIS_PROMPT = """You maintain the coral knowledge wiki in wiki/. Read wiki/_index.md for
conventions, then survey the current pages (concepts/, interventions/,
debates/, people/) and update the two synthesis pages:

1. wiki/synthesis/aging-model.md — the grand causal model. A mermaid
   diagram (or several) mapping how the aging mechanisms described across
   the wiki connect: upstream drivers, mediating pathways, outcomes, and
   which [[interventions]] act on which nodes. Make explicit, clearly
   labeled postulations about causal structure ("postulate: X because
   pages A/B imply..."), and mark weak links honestly. This page is a
   hypothesis under revision, not settled fact — revise it as pages accrue
   and note in the page when new evidence strengthened or weakened a link.

2. wiki/synthesis/practice-playbook.md — the actionable synthesis: what to
   do daily / weekly / monthly / periodically (labs, screenings), each item
   evidence-graded (strong / moderate / emerging / contested) and linked
   via [[wikilinks]] to the pages that justify it. Note where experts
   disagree rather than papering over it.

Both pages use frontmatter type: synthesis. Create them if absent. Do not
modify anything outside wiki/."""


def format_wiki() -> bool:
    """Deterministically normalize wiki formatting (prose wrapped at 80
    columns) — agents don't wrap consistently, so a formatter pass does."""
    result = subprocess.run(
        ["uv", "run", "mdformat", "--wrap", "80", str(WIKI_DIR)]
    )
    return result.returncode == 0


def run_synthesis() -> bool:
    result = subprocess.run(
        ["claude", "-p", SYNTHESIS_PROMPT, "--allowedTools", CLAUDE_ALLOWED_TOOLS]
    )
    return result.returncode == 0


def _batches(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def integrate_batch(staged_paths: list[str]) -> bool:
    result = subprocess.run(
        [
            "claude",
            "-p",
            integration_prompt(staged_paths),
            "--allowedTools",
            CLAUDE_ALLOWED_TOOLS,
        ]
    )
    return result.returncode == 0


def run_pipeline(
    videos: list[dict],
    conn: sqlite3.Connection,
    dry_run: bool = False,
    limit: int | None = None,
) -> dict:
    bootstrap_wiki()
    todo = unprocessed(conn, videos)
    if limit is not None:
        todo = todo[:limit]
    summary = {"new": len(todo), "integrated": 0, "failed_batches": 0}
    for batch in _batches(todo, BATCH_SIZE):
        staged = [str(stage(v)) for v in batch]
        if dry_run:
            print(f"[dry-run] would integrate: {[v['video_id'] for v in batch]}")
            for p in staged:
                Path(p).unlink()
            continue
        print(f"Integrating batch: {[v['title'][:50] for v in batch]}")
        if integrate_batch(staged):
            mark_processed(conn, batch)
            summary["integrated"] += len(batch)
            for p in staged:
                Path(p).unlink(missing_ok=True)
        else:
            summary["failed_batches"] += 1
            print(
                f"Batch failed — videos left unprocessed, staging kept: {staged}",
                file=sys.stderr,
            )
            break  # don't churn further batches after a failure

    if summary["integrated"] and not dry_run:
        print("Updating synthesis pages (aging model, practice playbook)")
        summary["synthesis_ok"] = run_synthesis()
        format_wiki()
    return summary


def collect_videos(
    channels_file: str | None, queries_file: str | None
) -> list[dict]:
    videos: list[dict] = []
    if channels_file:
        videos.extend(
            r
            for r in latest_videos_from_file(
                channels_file, n=15, include_transcripts=True
            )
            if "error" not in r
        )
    if queries_file:
        exclude = _read_channels_file(channels_file) if channels_file else None
        videos.extend(
            r
            for r in search_videos(
                _read_channels_file(queries_file),
                days=30,
                min_views=5000,
                min_subs=20000,
                exclude_channels=exclude,
                include_transcripts=True,
            )
            if "error" not in r
        )
    return videos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Integrate new videos into the coral knowledge wiki."
    )
    parser.add_argument("--channels-file", default="channels.txt")
    parser.add_argument("--queries-file", default="queries.txt")
    parser.add_argument("--channels-only", action="store_true")
    parser.add_argument("--queries-only", action="store_true")
    parser.add_argument("--limit-videos", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    channels = None if args.queries_only else args.channels_file
    queries = None if args.channels_only else args.queries_file
    videos = collect_videos(channels, queries)
    conn = connect()
    summary = run_pipeline(
        videos, conn, dry_run=args.dry_run, limit=args.limit_videos
    )
    print(
        f"\n{summary['new']} new videos; {summary['integrated']} integrated; "
        f"{summary['failed_batches']} failed batches"
    )
    return 1 if summary["failed_batches"] else 0


if __name__ == "__main__":
    sys.exit(main())
