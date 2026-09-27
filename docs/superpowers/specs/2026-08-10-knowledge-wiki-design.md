# Coral Knowledge Wiki — Design

**Date:** 2026-08-10
**Status:** Approved (entity-type structure, `wiki/` name, `claude -p` engine)

## Purpose

Turn coral from a retrieval tool into a knowledge system: new videos don't
get summarized in isolation — their content is **integrated into a living
wiki** of interlinked concept pages that accretes understanding over time
(the "LLM wiki" pattern, per Google's Open Knowledge Format / OKF).

## The wiki (`wiki/`)

An OKF-style bundle of markdown files, organized by **entity type** (domain
lives in tags, not folders — avoids misfiling cross-domain topics):

```
wiki/
  _index.md            # map of the wiki: sections, notable pages
  concepts/            # mechanisms & ideas (vo2-max, autophagy, zone-2-training)
  interventions/       # things you can do/take (rapamycin, creatine, hrt, norwegian-4x4)
  people/              # researchers & recurring voices (peter-attia, stacy-sims)
  debates/             # live disagreements (seed-oils, protein-timing)
  changelog.md         # dated entries: which pages changed, from which videos
```

Page conventions (enforced by the integration prompt, seeded by `_index.md`):

- YAML frontmatter: `type` (concept | intervention | person | debate —
  the only OKF-required field), `title`, `tags` (domains: longevity,
  nutrition, fitness, hormones, sleep-brain, skincare, urbanism), `updated`.
- Body: current understanding, organized by sub-topic; `[[wikilinks]]`
  (target page's filename stem) between related pages; a "Related" section
  listing backlinks the page owner knows about.
- **Every claim cites its source inline**: `(Channel — "Video Title",
  YYYY-MM-DD, [link](url))`. Conflicting claims are recorded as
  disagreements (ideally on a `debates/` page), never silently overwritten.
- Wiki growth is organic: no seeded skeleton pages; the first backfill run
  creates the initial pages.

### v3 register (2026-08-11 revision)

Pages are written as **textbook chapters**, not podcast digests: define
the subject, explain mechanisms from first principles, structure what is
known, weigh evidence — with videos as supporting references cited after
claims, never as the narrative spine. No sections named after people or
episodes outside `debates/`. Quotes must be verbatim transcript spans
(paraphrases go unquoted). Prose is written one paragraph per line and
never reflowed — width is the reader's (Obsidian's) concern.

### v2 conventions (2026-08-10 revision)

- Pages include **mermaid diagrams** wherever a mechanism/pathway/decision
  flow has structure worth seeing; a **Gaps & open questions** section
  (unknown/unmeasured — distinct from debates); a **Practical
  implications** section (what to do, at what cadence, evidence strength);
  and **unique perspectives** captured and attributed, not averaged away.
- New `wiki/synthesis/` section with two agent-maintained pages:
  `aging-model.md` (grand causal map with mermaid, explicit labeled
  postulations, revised as evidence accrues) and `practice-playbook.md`
  (daily/weekly/monthly/periodic actions, evidence-graded, wikilinked to
  justifying pages). A synthesis pass runs after every pipeline run that
  integrated at least one video.

## Seen-state store

`coral.db` (stdlib `sqlite3`, repo root, git-ignored): table
`processed_videos(video_id TEXT PRIMARY KEY, channel_handle TEXT,
title TEXT, published TEXT, integrated_at TEXT)`. A video is marked
processed only **after** the integration step that included it succeeds —
failed runs re-process, nothing is silently dropped.

## The updater (`update_wiki.py`)

One command: `uv run python update_wiki.py [--limit-videos N] [--dry-run]
[--channels-only | --queries-only] [--videos-per-channel N]`

An editorial refresh is available separately as `uv run python
update_wiki.py --refresh-wiki`. It retrieves no videos and audits every
existing page, restructuring accumulated material into subject-led textbook
chapters while preserving cited knowledge, uncertainty, and disagreements.

Evidence enrichment is a separate, web-enabled pass: `uv run python
update_wiki.py --enrich-wiki --pages 3 [--engine codex]`. It reads the
prioritized backlog in `wiki/_research-queue.md`, researches no more than the
requested number of items, and adds or improves textbook chapters using an
explicit evidence hierarchy. Episode links remain as provenance; underlying
papers, guidelines, and consensus statements are cited as Markdown footnotes
in each chapter's `References` section. Daily ingestion and evidence enrichment
remain separate so a retrieval failure cannot interrupt research work and a
research failure cannot incorrectly mark a video processed.
`uv run python update_wiki.py --validate-wiki` performs a deterministic
structural check that scholarly footnotes resolve, definitions are unique and
used, and every reference carries an evidence-type label and a linked source.
The daily ingestion job remains at 6:00 AM local time. A separate launchd job,
`com.coral.wiki-enrich`, runs Sundays at 7:00 AM local time, enriches two queue
items with Codex, and runs reference validation before reporting success.

Concept chapters are grouped by primary teaching domain under ten nested
folders, each with an `_index.md` reading path. Stem-based wikilinks remain
stable across moves, and `--validate-wiki` detects unresolved links or duplicate
stems. Evidence-review metadata distinguishes genuinely reviewed chapters from
legacy pages (`evidence_reviewed: never`, `review_status: review-due`). A monthly
audit on the first day at 8:00 AM checks stale or corrected evidence and
reconciles materially affected synthesis pages.

The writing engine defaults to `--engine auto`: Claude Code is attempted
first and a failed operation is retried with non-interactive Codex in the
workspace-write sandbox. `--engine claude` and `--engine codex` pin a single
engine. State is committed only after the selected engine (or fallback)
finishes successfully.

1. **Retrieve**: `latest_videos_from_file("channels.txt", n=15,
   include_transcripts=True)` and `search_videos` over `queries.txt`
   (days=30, min_views=5000, min_subs=20000, exclude channels.txt,
   transcripts on). Transcript cache makes repeat runs cheap.
2. **Diff**: drop videos already in `processed_videos`; drop videos with no
   transcript (retried next run, since None transcripts are never cached).
3. **Stage**: write each new video to `staging/<video_id>.md` (frontmatter:
   channel, title, published, url, views; body: video description followed by
   transcript). Descriptions are retained because creators often list the
   underlying papers, DOI links, and other source material there.
4. **Integrate**: in batches of 3 videos, invoke headless Claude Code:
   `claude -p <prompt> --allowedTools Read Glob Grep Write Edit`
   (cwd = repo root). The prompt instructs it to read `_index.md` and
   relevant pages, integrate the staged transcripts into `wiki/` following
   the page conventions, update `_index.md` when pages are added, and
   append a `changelog.md` entry. `--dry-run` prints the batches and
   prompts without invoking.
5. **Commit state**: on per-batch success (exit code 0), mark that batch's
   videos processed and delete their staging files. Batches are
   independent — a failed batch stops the run but keeps earlier batches'
   progress.
6. **Report**: print per-batch results and the changelog delta.

## Engine: `claude -p` (headless Claude Code)

- Uses the user's existing Claude Code auth — no API key management.
- Tool allowlist keeps it read/write on repo files only; no Bash.
- Batch size 3 keeps each invocation's context modest (~30k tokens of
  transcript + wiki pages it chooses to read).

## Testing

Offline: seen-state store CRUD + only-after-success semantics, staging file
format, batching, diff logic, prompt assembly — with the `claude`
invocation mocked (`subprocess.run` seam). Live: one small run
(`--limit-videos 3`) verifying real wiki pages appear with valid
frontmatter, wikilinks, citations, and a changelog entry, before any large
backfill.

## Out of scope (YAGNI)

Scheduling (separate step), email delivery, wiki rendering/serving,
automatic git commits of wiki changes (user reviews diffs), embedding
search over the wiki.
