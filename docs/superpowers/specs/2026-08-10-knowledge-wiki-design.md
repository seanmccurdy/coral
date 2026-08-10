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

## Seen-state store

`coral.db` (stdlib `sqlite3`, repo root, git-ignored): table
`processed_videos(video_id TEXT PRIMARY KEY, channel_handle TEXT,
title TEXT, published TEXT, integrated_at TEXT)`. A video is marked
processed only **after** the integration step that included it succeeds —
failed runs re-process, nothing is silently dropped.

## The updater (`update_wiki.py`)

One command: `uv run python update_wiki.py [--limit-videos N] [--dry-run]
[--channels-only | --queries-only]`

1. **Retrieve**: `latest_videos_from_file("channels.txt", n=15,
   include_transcripts=True)` and `search_videos` over `queries.txt`
   (days=30, min_views=5000, min_subs=20000, exclude channels.txt,
   transcripts on). Transcript cache makes repeat runs cheap.
2. **Diff**: drop videos already in `processed_videos`; drop videos with no
   transcript (retried next run, since None transcripts are never cached).
3. **Stage**: write each new video to `staging/<video_id>.md` (frontmatter:
   channel, title, published, url, views; body: transcript).
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
