"""Integrate new video transcripts into the coral knowledge wiki.

Retrieves new videos (channel pulls + query search), diffs against the
seen-state store, and feeds transcripts in small batches to headless
Claude Code (`claude -p`), which updates the OKF-style wiki in wiki/.
Videos are marked processed only after their batch integrates successfully.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from youtube_latest import latest_videos_from_file
from youtube_search import search_videos
from youtube_latest import _read_channels_file

DB_PATH = Path("coral.db")
STAGING_DIR = Path("staging")
WIKI_DIR = Path("wiki")
BATCH_SIZE = 3
CLAUDE_ALLOWED_TOOLS = "Read,Glob,Grep,Write,Edit"
ENGINES = ("auto", "claude", "codex")
CONCEPT_DOMAINS = {
    "aging-biology", "cardiometabolic", "brain-and-behavior", "immune-system",
    "exercise-and-movement", "nutrition-and-metabolism", "reproductive-health",
    "diagnostics-and-screening", "skin-and-hair", "environment-and-society",
}
PAGE_TYPES = {"concept", "intervention", "person", "debate", "hypothesis", "synthesis"}
REVIEW_STATUSES = {"current", "review-due", "under-review", "superseded", "contested"}
HYPOTHESIS_STATUSES = {"seed", "specified", "test-ready", "tested", "revised", "retired"}

_RESEARCH_QUEUE_TEMPLATE = """\
# Research queue

This is the prioritized evidence-enrichment backlog for the Coral textbook. The enrichment agent works from the first unchecked item, verifies claims against authoritative external sources, and records completion here. `P0` items are structural foundations; `P1` items close major clinical or system-coverage gaps.

## P0 — foundations of aging biology

- [ ] P0 Cellular senescence — define the phenotype, SASP, beneficial versus pathological roles, measurement limits, senolytic and senomorphic evidence, and connections to inflammation, cancer, fibrosis, and tissue repair.
- [ ] P0 Autophagy and lysosomal quality control — explain macroautophagy, mitophagy, flux, nutrient sensing, measurement, and intervention evidence.
- [ ] P0 mTOR and rapamycin — connect nutrient sensing, growth, repair, immune function, dosing hypotheses, animal longevity evidence, and human trial limits.
- [ ] P0 Mitochondrial dysfunction — cover energetics, dynamics, mitophagy, ROS signaling, exercise adaptation, and causal uncertainty in human aging.
- [ ] P0 Genomic instability and DNA repair — distinguish damage, repair pathways, somatic mutation, clonal expansion, and evidence for causal aging roles.
- [ ] P0 Loss of proteostasis — connect protein folding, chaperones, ubiquitin-proteasome function, aggregation, autophagy, and neurodegeneration.
- [ ] P0 Epigenetic alterations and reprogramming — explain clocks versus mechanisms, chromatin changes, partial reprogramming, and safety constraints.
- [ ] P0 Stem-cell exhaustion — cover tissue-specific stem-cell decline, niche effects, regeneration, cancer tradeoffs, and intervention evidence.
- [ ] P0 Telomere biology — distinguish replication limits, telomerase, short-telomere syndromes, population associations, and cancer tradeoffs.

## P1 — clinical and whole-system coverage

- [ ] P1 Bone health, osteoporosis, and fracture prevention.
- [ ] P1 Frailty, sarcopenia, falls, and functional reserve.
- [ ] P1 Kidney aging and chronic kidney disease prevention.
- [ ] P1 Liver aging and metabolic liver disease.
- [ ] P1 Oral health and its systemic connections.
- [ ] P1 Hearing, vision, cognition, and sensory loss.
- [ ] P1 Pulmonary aging and respiratory reserve.
- [ ] P1 Vaccination and immune aging.
- [ ] P1 Polypharmacy and deprescribing in older adults.

## Queue rules

- Preserve both kinds of attribution: episode citations document provenance; scholarly references document evidentiary support.
- Complete an item only after its chapter is integrated into the wiki, connected with wikilinks, and checked against the reference rules in `_index.md`.
- If an item is too broad for one pass, add narrower unchecked items directly beneath it and leave the parent unchecked.
- Add newly discovered cross-wiki gaps here with a priority and a concrete research question.
"""

_SYNTHESIS_STUBS = {
    "aging-model.md": ("Aging model", "A causal model under construction."),
    "practice-playbook.md": ("Practice playbook", "An evidence-graded practice guide under construction."),
}

_INDEX_TEMPLATE = """\
# Coral Wiki

A living knowledge base built from video transcripts. Organized by entity
type; domains (longevity, nutrition, fitness, hormones, sleep-brain,
skincare, urbanism) live in each page's `tags` frontmatter.

## Sections

- `concepts/` — mechanisms & ideas, organized into subject-area subfolders;
  each subfolder has an `_index.md` with a reading path
- `interventions/` — things you can do or take (e.g. rapamycin, creatine, hrt)
- `people/` — researchers & recurring voices (e.g. peter-attia)
- `debates/` — live disagreements (e.g. seed-oils)
- `hypotheses/` — mechanistic, falsifiable proposals for slowing aging;
  speculation is labeled and kept separate from practical guidance
- `synthesis/` — big-picture pages maintained across all videos:
  - `aging-model.md` — the grand causal map: how aging mechanisms connect
    (mermaid diagrams), which interventions act on which nodes, clearly
    labeled postulations about causality
  - `practice-playbook.md` — what to actually do daily / weekly / monthly /
    periodically, evidence-graded, linking to the pages that justify each

## Register: this wiki is a textbook, not a podcast digest

Every page teaches its subject the way a good textbook chapter does:
define the thing, explain the mechanism from first principles, build up
the structure of what is known, then weigh the evidence. The videos are
**references that support the exposition** — cited after the claims they
back — never the narrative spine. A page about NAD+ metabolism explains
NAD+ metabolism; it does not recount what was said on a podcast about
NAD+ metabolism. Extract the learning, then place it in the larger
system: how does this mechanism connect to the rest of the causal map
([[aging-model]]) and to the interventions that act on it?

Concretely: no sections named after people or episodes ("X's argument",
"Contrast: Y"), no play-by-play ("he goes on to say..."). Attribution
belongs in two places only: `debates/` pages, where who-holds-which-view
is the subject, and inline citations. A named expert's unique framing may
be taught as a framework (with citation) when it is genuinely the best
way to explain the material.

## Page conventions

- Frontmatter: `type` (concept | intervention | person | debate |
  hypothesis | synthesis), `title`, `tags` (domains), `updated`, `evidence_reviewed`,
  `evidence_cutoff`, `review_status`, and `review_interval`.
- Link related pages with [[wikilinks]] (the target file's stem); keep a
  "Related" section of links at the bottom of each page.
- Every claim cites its source inline:
  (Channel — "Video Title", YYYY-MM-DD, [link](url)).
- Scholarly enrichment uses Markdown footnotes and a `## References`
  section. Preserve episode citations as provenance; they do not replace
  the papers, guidelines, or consensus statements that support a claim.
- Link and retraction checks establish bibliographic integrity only; a
  claim-level review must also verify that each source entails its nearby
  statement. P0 pages require an adversarial second pass seeking negative
  evidence, harms, contradictory guidance, alternate explanations,
  population mismatch, and non-independent sources before becoming current.
- Set review cadence by consequence and volatility: normally 90–180 days
  for labels, safety, active guidance, diagnostics, and fast-moving trials;
  365 days for consequential stable clinical evidence; up to 730 days for
  mature foundational material. Unresolved P0 material remains under review.
- **Diagrams**: when a mechanism, pathway, or system has structure (causal
  chains, feedback loops, decision flows), draw it as a ```mermaid block
  (flowchart or graph) rather than describing it only in prose.
- **Gaps & open questions**: each substantive page keeps a section for
  what is unknown, unmeasured, or understudied — distinct from debates
  (contested claims); a gap is a question nobody has answered yet.
- **Hypothesis development**: promote an open question into `hypotheses/`
  only when it can be expressed as a causal proposal with discriminating
  predictions. Keep speculation out of the practice playbook. Each hypothesis
  states its rationale, alternatives, experiment, endpoints, failure criteria,
  confounders, safety boundary, and status; negative evidence revises or retires it.
- **Practical implications**: each concept/intervention page states what a
  person should actually do with this knowledge (and at what cadence),
  with the strength of evidence behind it.
- **Unique perspectives**: contrarian or minority takes are captured and
  attributed to their proponent, not averaged into consensus.
- Conflicting claims are recorded as disagreements (prefer a debates/
  page), never silently overwritten.
- **Synthesis impact**: every writing pass explicitly decides whether its
  evidence materially changes a causal link, evidence grade, recommendation,
  safety warning, or major uncertainty in a synthesis page. Update synthesis
  immediately when it does; otherwise report `no material change`. Never edit
  synthesis merely to mention that a new chapter exists.
- **Corrections**: never silently replace a formerly supported conclusion.
  State what changed and why in an `Evidence update` callout, preserve useful
  historical context, mark retracted or superseded sources, update affected
  synthesis, and record the correction in the changelog.
- Formatting: do not hard-wrap prose — write each paragraph as one line
  and let the reader's editor (Obsidian) soft-wrap. Never reflow existing
  text just to change its width.

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
    queue = WIKI_DIR / "_research-queue.md"
    if not queue.exists():
        queue.write_text(_RESEARCH_QUEUE_TEMPLATE)
    today = date.today().isoformat()
    for filename, (title, body) in _SYNTHESIS_STUBS.items():
        path = WIKI_DIR / "synthesis" / filename
        if not path.exists():
            path.write_text(
                f"---\ntype: synthesis\ntitle: {title}\ntags: [longevity]\n"
                f"updated: {today}\nevidence_reviewed: never\nevidence_cutoff: unknown\n"
                f"review_status: review-due\nreview_interval: 180d\n---\n\n# {title}\n\n{body}\n"
            )


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
        "## Video description\n\n"
        f"{video.get('description') or ''}\n\n"
        "## Transcript\n\n"
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

0. REGISTER — the most important rule: write like a textbook, not a
   podcast digest. Each page TEACHES its subject: define it, explain the
   mechanism from first principles, structure what is known, weigh the
   evidence and say how strong it is. The video is a reference supporting
   that exposition (cited after the claims it backs), never the narrative.
   No sections named after people or episodes, no "X argues... Y responds"
   play-by-play outside debates/ pages. Extract the learning; then relate
   it to the whole system (which causal nodes it touches, which
   interventions act on it).
1. Identify the substantive claims, protocols, findings, positions — and
   the genuinely unique or contrarian perspectives, attributed to their
   proponents.
2. Update the relevant existing pages under wiki/concepts/,
   wiki/interventions/, wiki/people/, wiki/debates/ — or create new pages
   where a topic has none. Follow the frontmatter and page conventions
   from wiki/_index.md exactly, including per page:
   - place a new concept in its primary subject-area subfolder and update
     that subfolder's `_index.md`; never add concept files to concepts/ root
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
   QUOTE INTEGRITY: text inside quotation marks must be a verbatim span
   from the staged transcript — re-check the transcript before writing any
   quote. If you are compressing or paraphrasing, write it WITHOUT
   quotation marks. A paraphrase presented as a quote is a fabrication.
4. When a new claim conflicts with something already on a page, record the
   disagreement explicitly (move contested points to a debates/ page if
   substantial) — never silently overwrite or drop either side.
5. Maintain [[wikilinks]] between related pages and each page's Related
   section. Update wiki/_index.md's Notable pages list if you add pages.
6. Append one entry to wiki/changelog.md under today's date: each video on
   one line with the pages it created/updated.

Before finishing, perform and report a synthesis-impact check for
`aging-model`, `practice-playbook`, and any other synthesis page. Update only
where a causal link, evidence grade, recommendation, safety warning, or major
uncertainty materially changed. Set the evidence-review frontmatter on pages
whose external evidence was actually reviewed.

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

Both pages use frontmatter type: synthesis, and the wiki's textbook
register (see _index.md): teach and explain; cite pages/sources as
references, don't narrate who said what. Create them if absent. Do not
modify anything outside wiki/."""


REFRESH_PROMPT = """Refresh the existing coral knowledge wiki in wiki/ so it reads as a
coherent textbook rather than a collection of podcast or interview notes.
Read wiki/_index.md first, then audit every Markdown page under wiki/.

For each substantive page:

1. Reorganize around the subject itself. Begin with a clear definition and
   why the subject matters, explain mechanisms from first principles, then
   connect the subject to the larger system through [[wikilinks]]. Organize
   by concepts and causal structure, never by the order of a conversation.
2. Remove podcast-summary narration and episode chronology: constructions
   such as "X says", "Y explains", "the conversation turns to", or sections
   named after a speaker or episode. Preserve the underlying claim and its
   inline citation. Attribution belongs in citations, in genuinely useful
   named frameworks, and on debates/ pages where positions are the subject.
3. Synthesize repeated or fragmented claims into one explanation. Do not
   merely shorten the page. Preserve meaningful distinctions, uncertainty,
   minority views, practical detail, and every source that still supports a
   retained claim. Never invent a fact, citation, quotation, or consensus.
4. Make evidence legible: distinguish established knowledge from plausible
   mechanisms, observational associations, expert inference, and contested
   claims. Move substantial disagreements to debates/ pages and link them.
5. Relate each topic to the whole knowledge system: upstream causes,
   downstream effects, interacting concepts, and interventions that act on
   it. Add a mermaid diagram only when it clarifies a real mechanism, causal
   map, feedback loop, or decision process.
6. Ensure concept and intervention pages have useful "Practical implications",
   "Gaps & open questions", and "Related" sections. These
   sections must contain topic-specific substance, not boilerplate.
7. Keep one paragraph per line without hard-wrapping. Maintain valid
   frontmatter and update each materially revised page's `updated` date.

This is an editorial refactor of existing knowledge, not a new research
pass: use only claims and sources already present in the wiki. Do not erase
unsupported-looking material silently; qualify it or place it under an open
question. Update wiki/_index.md after the audit and append one concise,
dated refresh entry to wiki/changelog.md. Finally update the synthesis pages
so [[aging-model]] and [[practice-playbook]] reflect the refreshed chapters.
Do not modify anything outside wiki/."""


AUDIT_PROMPT = """Perform the monthly evidence-correction and synthesis audit of wiki/.
Read wiki/_index.md, wiki/_research-queue.md, wiki/_review-queue.md,
wiki/_dependencies.json, wiki/_sources.json, and the generated freshness report.
Review only the bounded unchecked pages in `_review-queue.md`. When correcting a
page, use `_dependencies.json` to inspect every direct consumer and especially
each listed synthesis consumer; update affected pages or document why no change
is needed. Treat any source marked retracted as an urgent correction.
Use web search to review pages marked review-due, plus any current page whose
claims may have been superseded, contradicted, retracted, or changed by a major
guideline or trial. Prioritize clinical recommendations and safety claims.

Use two explicit passes for each P0 page. First construct the strongest fair
evidence synthesis. Then reset to an adversarial question: what would falsify or
materially narrow this conclusion? Search specifically for negative trials,
contradictory guidance, harms, alternate causal explanations, population or
duration mismatch, conflicts of interest, and reports derived from the same
cohort. Preserve credible conflicts in an `Evidence conflicts` or dated
`Evidence update` section. Link resolution and retraction status do not prove
that a citation supports its adjacent claim.

Never silently overwrite history. For a material correction, revise the current
conclusion, add a dated `Evidence update` callout explaining what changed and
why, retain still-useful historical context, label retracted or superseded
sources, propagate the correction to affected synthesis pages, and record it in
changelog.md. Update `evidence_reviewed`, `evidence_cutoff`, `review_status`, and
`review_interval` only when a real evidence review occurred. Check a queue item
only after its material concept, outcome, and protocol claims were reviewed
against the strongest applicable evidence; opening, summarizing, or merely
flagging a page does not complete it. For every completed page, apply the claim
states, protocol-admission, applicability, outcome-hierarchy, absolute-effect,
conflict-of-interest, contradiction, and retirement rules in `_index.md`.

Reconcile every synthesis page against the current chapters. Add missing
material links, remove stale recommendations, and correct evidence grades, but
do not churn prose when there is no material change. Finish with a
synthesis-impact report listing each synthesis page as updated or no material change and
why. Do not modify anything outside wiki/."""


def hypothesis_ideation_prompt() -> str:
    return """Run only the ideation stage of the weekly Coral hypothesis workshop.
Read the required wiki contract, then wiki/hypotheses/_index.md and
wiki/hypotheses/_idea-queue.md. Do not research or promote a hypothesis in this pass.
Do not read the aging model, research queue, or all wiki gaps, and do not run broad recursive
searches. Inspect at most six chapters linked from the current nursery.

Edit _idea-queue.md to add exactly three distinct human-direct seeds unless twelve are already
active. If full, archive or merge the three weakest or most redundant seeds before adding three.
Every seed must include the complete seed format. Rank all active seeds consistently. Save the
nursery edit. A run with no nursery change is a failure. Do not modify anything outside wiki/.
"""


def hypothesis_prompt(max_new: int) -> str:
    return f"""Run only the evidence-review stage of the weekly Coral hypothesis workshop.
Read the required wiki contract, wiki/hypotheses/_index.md,
wiki/hypotheses/_hypothesis-template.md, and wiki/hypotheses/_idea-queue.md.
Choose only the highest-ranked active seed. Inspect no more than six relevant wiki chapters
and eight external sources. Do not generate additional seeds in this pass.

First review every existing published hypothesis. Revise its evidence ledger, status, scope,
or failure criteria only when new evidence or a stronger formulation warrants it; preserve
negative and superseded reasoning. Then identify high-leverage connections between documented
gaps, established interventions, implementation problems, and tradeoffs across the aging system.

Scope is human-direct. Develop ideas that could improve human health or function through
low-risk behavior, exercise, nutrition, sleep, adherence, timing, measurement, prevention,
or care delivery. Prefer designs feasible without a wet lab: randomized N-of-1, pragmatic,
factorial, crossover, prospective cohort, or secondary-data studies using validated human
outcomes. Do not generate hypotheses whose decisive test requires cells, animals, gene editing,
novel drug targets, unapproved compounds, or specialized basic/translational laboratory work.
Do not propose starting, stopping, or changing prescription treatment outside clinical care.
For promotion, use guidelines, systematic reviews, registered human trials, and primary
PubMed-indexed human studies as evidence. Podcast and video material may identify a question
or document provenance, but it cannot establish the hypothesis rationale or expected effect.

Maintain a bounded idea nursery in wiki/hypotheses/_idea-queue.md. Generate exactly three distinct
new candidate seeds per run unless twelve active seeds already exist; when full, prune, merge,
promote, or archive before adding replacements. Retain no more than twelve active seeds. A seed
is explicitly unreviewed—not a published hypothesis—and must include a one-sentence causal
idea, source wiki gaps, why it might matter, its strongest alternative explanation, one
discriminating observation, major safety concern, and the research needed before promotion.
Rank active seeds by leverage, novelty, testability, evidence distance, and safety. Archive
rejected or promoted seeds in the same file with a dated reason so the nursery has memory.

After refreshing the nursery, develop its strongest candidate. Create no more than {max_new} new hypothesis
page(s), and create none when no candidate meets
the entry criteria. Do not optimize for novelty count. A published candidate must:

1. state one precise, causal, falsifiable claim;
2. distinguish direct evidence, extrapolation, and assumptions with citations;
3. include a Mermaid mechanistic model showing the leveraged behavioral, physiological, or
   delivery-system node, causal chain, competing
   pathway, measurable endpoints, and major harm branch; label evidence strength on links;
4. make quantitative predictions where feasible, including one that separates it from the
   strongest alternative explanation and one adverse or paradoxical prediction;
5. propose the safest decisive test with population/model, comparator, endpoints, duration,
   controls, confounders, and analysis;
6. precommit to evidence that would support, narrow, revise, or retire it;
7. distinguish molecular markers, function, disease, healthspan, and lifespan;
8. state safety, off-target, cancer, immune, repair, and translation boundaries; and
9. use every required section and `hypothesis_status` defined by the template.

Its primary endpoint must be a human functional, symptomatic, behavioral, clinical, or
quality-of-life outcome. Biomarkers and device metrics may be secondary or mechanistic
measurements, but a biomarker-only improvement is insufficient for promotion.

Do not turn a hypothesis into personal advice, add it to practice-playbook, or imply that
mechanistic plausibility establishes benefit. Update wiki/hypotheses/_index.md's current list
and add a dated changelog entry naming created, revised, or retired hypotheses. Perform the
synthesis-impact check: update aging-model only if the evidence review materially changes its
causal map or uncertainty, never merely because a hypothesis was created. Do not modify
anything outside wiki/.
"""


def enrichment_prompt(pages: int) -> str:
    return f"""Enrich the Coral textbook in wiki/ with authoritative external evidence.
Read wiki/_index.md and wiki/_research-queue.md first. Select the first {pages}
unchecked research items in priority order and complete no more than {pages} items.
An item may require improving an existing chapter or creating a missing one.

Use web search to find and open the underlying scholarly sources. Prefer this
evidence hierarchy, and identify the design accurately in the prose:

1. Clinical guidelines and scientific consensus statements
2. Systematic reviews and meta-analyses
3. Randomized controlled trials
4. Prospective observational studies
5. Mechanistic human studies
6. Animal studies
7. Cell and ex-vivo studies
8. Expert interpretation
9. Commercial claims

Use primary or authoritative sources wherever possible: the original paper at
its DOI or PubMed record, government or professional-society guidelines, and
official trial records. A review may establish context but must not be presented
as if it were the underlying experiment. Do not cite search-result pages,
AI-generated summaries, or a podcast as proof of a scientific claim. Verify that
every source actually supports the nearby statement. Never invent a reference,
DOI, PMID, author, study design, sample size, result, or consensus.

Write as a textbook: define the subject, teach mechanisms from first principles,
distinguish human outcomes from biomarkers and mechanistic hypotheses, give
absolute effects when the source supports them, and connect the chapter to the
larger system with [[wikilinks]]. State uncertainty and external validity limits.
Preserve existing episode citations as provenance and useful expert framing.

For scholarly evidence, use stable Markdown footnotes such as [^smith-2024] at
the supported claim and define each exactly once under `## References`. Each
reference must include authors or organization, title, publication/year, the
evidence type in brackets (for example `[systematic review]` or `[RCT]`), and a
direct DOI, PubMed, guideline, or official-record link. Do not leave bare URLs.
Ensure footnote IDs are unique within a file, every use has a definition, every
definition is used, and each material evidence claim has a nearby citation.

Keep the chapter conventions in _index.md, including frontmatter, practical
implications, gaps, related links, and diagrams only where structurally useful.
Place new concept chapters in their primary subject-area subfolder and update
that folder's `_index.md`; never add concept files directly to concepts/ root.
Mark a queue item complete only when the chapter and references satisfy these
rules; otherwise split it into narrower unchecked tasks. Update _index.md when
adding a notable page and append a concise dated entry to changelog.md.
Set evidence-review frontmatter for every researched page. Finish with an
explicit synthesis-impact check for each synthesis page; update it only if a
causal link, evidence grade, recommendation, safety warning, or major uncertainty
materially changed, and report the reason either way.
Do not modify anything outside wiki/."""


def run_agent(prompt: str, engine: str = "auto", web_search: bool = False) -> bool:
    """Run a wiki-editing agent, falling back to Codex in auto mode."""
    if engine not in ENGINES:
        raise ValueError(f"unknown engine: {engine}")

    if engine in ("auto", "claude"):
        allowed_tools = CLAUDE_ALLOWED_TOOLS
        if web_search:
            allowed_tools += ",WebSearch,WebFetch"
        result = subprocess.run(["claude", "-p", prompt, "--allowedTools", allowed_tools])
        if result.returncode == 0:
            return True
        if engine == "claude":
            return False
        print("Claude failed; retrying this operation with Codex", file=sys.stderr)

    codex_command = ["codex", "--ask-for-approval", "never"]
    if web_search:
        codex_command.append("--search")
    codex_command.extend(
        [
            "exec",
            "--sandbox",
            "workspace-write",
            "-C",
            str(Path.cwd()),
            prompt,
        ]
    )
    result = subprocess.run(codex_command)
    return result.returncode == 0


def validate_wiki() -> list[str]:
    return validate_wiki_references() + validate_wiki_links() + validate_wiki_schema()


def run_agent_transactional(prompt: str, engine: str = "auto", web_search: bool = False, require_changes: bool = False) -> bool:
    """Commit agent edits only when the agent and all validators succeed."""
    with tempfile.TemporaryDirectory(prefix="coral-wiki-") as temporary:
        snapshot = Path(temporary) / "wiki"
        existed = WIKI_DIR.exists()
        if existed:
            shutil.copytree(WIKI_DIR, snapshot)
        if run_agent(prompt, engine, web_search=web_search):
            before = {str(path.relative_to(snapshot)): path.read_bytes() for path in snapshot.rglob("*") if path.is_file()} if existed else {}
            after = {str(path.relative_to(WIKI_DIR)): path.read_bytes() for path in WIKI_DIR.rglob("*") if path.is_file()} if WIKI_DIR.exists() else {}
            if before == after and require_changes:
                print("Agent made no wiki changes; treating run as failed", file=sys.stderr)
            else:
                errors = validate_wiki()
                if not errors:
                    return True
                print("Wiki validation failed; restoring snapshot:\n" + "\n".join(errors), file=sys.stderr)
        if WIKI_DIR.exists():
            shutil.rmtree(WIKI_DIR)
        if existed:
            shutil.copytree(snapshot, WIKI_DIR)
        return False


def run_synthesis(engine: str = "auto") -> bool:
    return run_agent_transactional(SYNTHESIS_PROMPT, engine)


def refresh_wiki(engine: str = "auto") -> bool:
    """Retrofit the current corpus to the wiki's textbook register."""
    bootstrap_wiki()
    return run_agent_transactional(REFRESH_PROMPT, engine)


def enrich_wiki(pages: int = 3, engine: str = "auto") -> bool:
    """Research and enrich the highest-priority wiki gaps."""
    if pages < 1:
        raise ValueError("pages must be at least 1")
    bootstrap_wiki()
    return run_agent_transactional(enrichment_prompt(pages), engine, web_search=True)


def develop_hypotheses(max_new: int = 1, engine: str = "auto", dry_run: bool = False) -> bool:
    """Run a bounded, evidence-seeking hypothesis workshop."""
    if max_new < 1:
        raise ValueError("max_new must be at least 1")
    bootstrap_wiki()
    prompt = hypothesis_prompt(max_new)
    if dry_run:
        print(hypothesis_ideation_prompt())
        print("\n--- evidence-review pass ---\n")
        print(prompt)
        return True
    if not run_agent_transactional(hypothesis_ideation_prompt(), engine, require_changes=True):
        return False
    return run_agent_transactional(prompt, engine, web_search=True)


def validate_wiki_references() -> list[str]:
    """Return structural errors in scholarly footnotes and reference sections."""
    errors: list[str] = []
    use_pattern = re.compile(r"\[\^([^\]]+)\](?!:)")
    definition_pattern = re.compile(r"^\[\^([^\]]+)\]:\s*(.+)$", re.MULTILINE)
    for path in WIKI_DIR.rglob("*.md"):
        text = path.read_text()
        definitions = definition_pattern.findall(text)
        if not definitions and "## References" not in text:
            continue
        relative = path.relative_to(WIKI_DIR)
        if definitions and "## References" not in text:
            errors.append(f"{relative}: footnotes exist without a References section")
        uses = use_pattern.findall(text)
        use_ids = set(uses)
        definition_ids = [identifier for identifier, _ in definitions]
        for identifier in sorted(use_ids - set(definition_ids)):
            errors.append(f"{relative}: [^{identifier}] has no definition")
        for identifier in sorted(set(definition_ids) - use_ids):
            errors.append(f"{relative}: [^{identifier}] is defined but unused")
        for identifier in sorted({x for x in definition_ids if definition_ids.count(x) > 1}):
            errors.append(f"{relative}: [^{identifier}] is defined more than once")
        for identifier, reference in definitions:
            if not re.search(r"\[[^\]]+\]\(https?://[^)]+\)", reference):
                errors.append(f"{relative}: [^{identifier}] lacks a linked source")
            before_first_link = reference.split("](", 1)[0]
            labels = re.findall(r"\[([^\]]+)\]", before_first_link)
            if not labels:
                errors.append(f"{relative}: [^{identifier}] lacks an evidence-type label")
    return errors


def validate_wiki_links() -> list[str]:
    """Return unresolved and ambiguous stem-based wikilinks."""
    errors: list[str] = []
    by_stem: dict[str, list[Path]] = {}
    for path in WIKI_DIR.rglob("*.md"):
        if path.name == "_index.md":
            continue
        by_stem.setdefault(path.stem, []).append(path)
    for stem, paths in sorted(by_stem.items()):
        if len(paths) > 1:
            locations = ", ".join(str(p.relative_to(WIKI_DIR)) for p in paths)
            errors.append(f"ambiguous page stem {stem}: {locations}")
    pattern = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
    for path in WIKI_DIR.rglob("*.md"):
        for target in pattern.findall(path.read_text()):
            stem = Path(target.strip()).stem
            if stem == "wikilinks":
                continue
            if stem not in by_stem:
                errors.append(f"{path.relative_to(WIKI_DIR)}: unresolved [[{target}]]")
    return errors


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    block = text.split("\n---\n", 1)[0][4:]
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"^([\w-]+):\s*(.+)$", block, re.MULTILINE)}


def validate_wiki_schema() -> list[str]:
    """Validate page metadata, required sections, and concept taxonomy."""
    errors: list[str] = []
    concepts = WIKI_DIR / "concepts"
    if concepts.exists():
        for path in concepts.glob("*.md"):
            errors.append(f"{path.relative_to(WIKI_DIR)}: concepts root may contain no chapters")
        for directory in concepts.iterdir():
            if directory.is_dir() and directory.name not in CONCEPT_DOMAINS:
                errors.append(f"concepts/{directory.name}: unknown concept domain")
            if directory.is_dir() and not (directory / "_index.md").exists():
                errors.append(f"concepts/{directory.name}: missing _index.md")
    required = {"type", "title", "tags", "updated", "evidence_reviewed", "evidence_cutoff", "review_status", "review_interval"}
    for path in WIKI_DIR.rglob("*.md"):
        if path.name.startswith("_") or path.name == "changelog.md":
            continue
        relative = path.relative_to(WIKI_DIR)
        meta = _frontmatter(path.read_text())
        missing = sorted(required - meta.keys())
        if missing:
            errors.append(f"{relative}: missing frontmatter {', '.join(missing)}")
            continue
        if meta["type"] not in PAGE_TYPES:
            errors.append(f"{relative}: invalid type {meta['type']}")
        expected_type = {
            "concepts": "concept", "interventions": "intervention",
            "people": "person", "debates": "debate", "hypotheses": "hypothesis",
            "synthesis": "synthesis",
        }.get(relative.parts[0], "")
        if meta["type"] != expected_type:
            errors.append(f"{relative}: type {meta['type']} does not match section {expected_type}")
        if meta["review_status"] not in REVIEW_STATUSES:
            errors.append(f"{relative}: invalid review_status {meta['review_status']}")
        if not re.fullmatch(r"\d+d", meta["review_interval"]):
            errors.append(f"{relative}: invalid review_interval {meta['review_interval']}")
        if meta["evidence_reviewed"] != "never" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", meta["evidence_reviewed"]):
            errors.append(f"{relative}: invalid evidence_reviewed {meta['evidence_reviewed']}")
        if meta["review_status"] == "current" and meta["evidence_reviewed"] == "never":
            errors.append(f"{relative}: current page has never been evidence reviewed")
        if meta["type"] in {"concept", "intervention"}:
            text = path.read_text()
            for heading in ("## Practical implications", "## Gaps & open questions", "## Related"):
                if heading not in text:
                    errors.append(f"{relative}: missing {heading}")
        if meta["type"] == "hypothesis":
            text = path.read_text()
            if "hypothesis_status" not in meta:
                errors.append(f"{relative}: missing frontmatter hypothesis_status")
            elif meta["hypothesis_status"] not in HYPOTHESIS_STATUSES:
                errors.append(f"{relative}: invalid hypothesis_status {meta['hypothesis_status']}")
            for heading in (
                "## Causal rationale", "## Mechanistic model", "## Testable predictions", "## Proposed test",
                "## What would change our minds", "## Safety and translation boundary",
                "## Related",
            ):
                if heading not in text:
                    errors.append(f"{relative}: missing {heading}")
            if "## Mechanistic model" in text and not re.search(
                r"## Mechanistic model.*?```mermaid\s+.+?```", text, re.DOTALL
            ):
                errors.append(f"{relative}: Mechanistic model must contain a Mermaid diagram")
    return errors


def freshness_report(today: date | None = None) -> tuple[str, list[str]]:
    """Build a deterministic report of missing or overdue evidence reviews."""
    today = today or date.today()
    rows: list[tuple[str, str, str]] = []
    errors: list[str] = []
    for path in WIKI_DIR.rglob("*.md"):
        if path.name.startswith("_") or path.name == "changelog.md":
            continue
        text = path.read_text()
        relative = str(path.relative_to(WIKI_DIR))
        reviewed_match = re.search(r"^evidence_reviewed:\s*(\d{4}-\d{2}-\d{2}|never)$", text, re.MULTILINE)
        interval_match = re.search(r"^review_interval:\s*(\d+)d$", text, re.MULTILINE)
        status_match = re.search(r"^review_status:\s*([\w-]+)$", text, re.MULTILINE)
        if not reviewed_match or not interval_match or not status_match:
            errors.append(f"{relative}: incomplete evidence-review metadata")
            rows.append((relative, "missing", "review-due"))
            continue
        if reviewed_match.group(1) == "never":
            rows.append((relative, "now", "review-due"))
            continue
        reviewed = date.fromisoformat(reviewed_match.group(1))
        due = reviewed + timedelta(days=int(interval_match.group(1)))
        computed = "review-due" if due <= today else status_match.group(1)
        rows.append((relative, due.isoformat(), computed))
    report = "# Wiki freshness report\n\nGenerated: " + today.isoformat() + "\n\n"
    report += "| Page | Review due | Status |\n|---|---:|---|\n"
    report += "".join(f"| `{page}` | {due} | {status} |\n" for page, due, status in sorted(rows))
    return report, errors


def build_dependency_graph() -> dict[str, dict[str, list[str]]]:
    """Build reverse wikilink dependencies, highlighting synthesis consumers."""
    pages = {p.stem: p for p in WIKI_DIR.rglob("*.md") if not p.name.startswith("_")}
    inbound: dict[str, set[str]] = {stem: set() for stem in pages}
    synthesis: dict[str, set[str]] = {stem: set() for stem in pages}
    pattern = re.compile(r"\[\[([^\]|#]+)")
    for source_stem, path in pages.items():
        for target in pattern.findall(path.read_text()):
            target_stem = Path(target.strip()).stem
            if target_stem in inbound:
                inbound[target_stem].add(source_stem)
                if path.relative_to(WIKI_DIR).parts[0] == "synthesis":
                    synthesis[target_stem].add(source_stem)
    return {stem: {"inbound": sorted(inbound[stem]), "synthesis": sorted(synthesis[stem])} for stem in sorted(pages)}


def write_dependency_graph() -> Path:
    path = WIKI_DIR / "_dependencies.json"
    path.write_text(json.dumps(build_dependency_graph(), indent=2) + "\n")
    return path


def build_source_registry() -> dict[str, dict]:
    """Extract DOI/PubMed sources and the pages that depend on them."""
    registry: dict[str, dict] = {}
    definition_pattern = re.compile(r"^\[\^([^\]]+)\]:\s*(.+)$", re.MULTILINE)
    doi_pattern = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
    pmid_pattern = re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)")
    for path in WIKI_DIR.rglob("*.md"):
        relative = str(path.relative_to(WIKI_DIR))
        for _, reference in definition_pattern.findall(path.read_text()):
            doi = doi_pattern.search(reference)
            pmid = pmid_pattern.search(reference)
            if not doi and not pmid:
                continue
            doi_value = doi.group(0).rstrip(".,;") if doi else None
            while doi_value and doi_value.endswith(")") and doi_value.count(")") > doi_value.count("("):
                doi_value = doi_value[:-1]
            key = f"doi:{doi_value.lower()}" if doi_value else f"pmid:{pmid.group(1)}"
            item = registry.setdefault(key, {"doi": doi_value, "pmid": pmid.group(1) if pmid else None, "citation": reference, "pages": [], "status": "unverified", "checked": None})
            item["pages"].append(relative)
    for item in registry.values():
        item["pages"] = sorted(set(item["pages"]))
    return dict(sorted(registry.items()))


def write_source_registry(check: bool = False) -> tuple[Path, list[str]]:
    registry = build_source_registry()
    path = WIKI_DIR / "_sources.json"
    if path.exists() and not check:
        try:
            previous = json.loads(path.read_text())
            for key, item in registry.items():
                if key in previous:
                    item["status"] = previous[key].get("status", item["status"])
                    item["checked"] = previous[key].get("checked")
        except json.JSONDecodeError:
            pass
    warnings: list[str] = []
    if check:
        for key, item in registry.items():
            encoded_doi = urllib.parse.quote(item["doi"] or "", safe="")
            url = f"https://api.crossref.org/works/{encoded_doi}?mailto=seanmccurdy@users.noreply.github.com" if item["doi"] else f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/"
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "coral-wiki/1.0 (source verification)"})
                with urllib.request.urlopen(request, timeout=15) as response:
                    body = response.read().decode("utf-8", errors="replace")
                item["status"] = "verified"
                if item["doi"]:
                    message = json.loads(body).get("message", {})
                    updates = message.get("update-to", []) + message.get("relation", {}).get("is-retracted-by", [])
                    if any("retract" in json.dumps(update).lower() for update in updates):
                        item["status"] = "retracted"
                        warnings.append(f"{key}: Crossref reports a retraction")
                elif "Retracted Publication" in body or "Retraction of Publication" in body:
                    item["status"] = "retracted"
                    warnings.append(f"{key}: PubMed reports a retraction")
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                if item["pmid"]:
                    try:
                        fallback = urllib.request.Request(
                            f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/",
                            headers={"User-Agent": "coral-wiki/1.0 (source verification)"},
                        )
                        with urllib.request.urlopen(fallback, timeout=15) as response:
                            body = response.read().decode("utf-8", errors="replace")
                        item["status"] = "retracted" if "Retracted Publication" in body else "verified-pubmed"
                        if item["status"] == "retracted":
                            warnings.append(f"{key}: PubMed reports a retraction")
                    except (urllib.error.URLError, TimeoutError) as fallback_exc:
                        item["status"] = "unresolved"
                        warnings.append(f"{key}: source check failed: {exc}; PubMed fallback: {fallback_exc}")
                else:
                    item["status"] = "unresolved"
                    warnings.append(f"{key}: source check failed: {exc}")
            item["checked"] = date.today().isoformat()
            time.sleep(0.2)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n")
    return path, warnings


def write_review_queue(limit: int = 8) -> Path:
    """Prioritize a bounded monthly review using risk and synthesis dependence."""
    dependencies = build_dependency_graph()
    candidates: list[tuple[int, str, str]] = []
    for path in WIKI_DIR.rglob("*.md"):
        if path.name.startswith("_") or path.name == "changelog.md":
            continue
        meta = _frontmatter(path.read_text())
        if meta.get("review_status") != "review-due" and meta.get("evidence_reviewed") != "never":
            continue
        relative = str(path.relative_to(WIKI_DIR))
        score = 0
        if relative.startswith(("interventions/", "debates/")):
            score += 40
        if "safety" in path.read_text().lower() or "do not" in path.read_text().lower():
            score += 20
        score += 15 * len(dependencies.get(path.stem, {}).get("synthesis", []))
        score += min(10, len(dependencies.get(path.stem, {}).get("inbound", [])))
        candidates.append((-score, relative, path.stem))
    selected = sorted(candidates)[:limit]
    output = "# Monthly review queue\n\n"
    output += f"Bounded to {limit} highest-risk review-due pages. Generated: {date.today().isoformat()}.\n\n"
    for negative_score, relative, stem in selected:
        consumers = dependencies.get(stem, {}).get("synthesis", [])
        output += f"- [ ] risk={abs(negative_score):03d} `{relative}` — synthesis consumers: {', '.join(consumers) or 'none'}\n"
    path = WIKI_DIR / "_review-queue.md"
    path.write_text(output)
    return path


def audit_wiki(engine: str = "auto", dry_run: bool = False, pages: int = 8) -> bool:
    """Run the monthly stale-evidence, correction, and synthesis audit."""
    bootstrap_wiki()
    report, _ = freshness_report()
    report_path = WIKI_DIR / "_freshness-report.md"
    report_path.write_text(report)
    write_dependency_graph()
    write_source_registry(check=False)
    write_review_queue(pages)
    if dry_run:
        print(AUDIT_PROMPT)
        return True
    return run_agent_transactional(AUDIT_PROMPT, engine, web_search=True)


def _batches(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def integrate_batch(staged_paths: list[str], engine: str = "auto") -> bool:
    return run_agent_transactional(integration_prompt(staged_paths), engine)


def run_pipeline(
    videos: list[dict],
    conn: sqlite3.Connection,
    dry_run: bool = False,
    limit: int | None = None,
    engine: str = "auto",
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
        if integrate_batch(staged, engine):
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
        summary["synthesis_ok"] = run_synthesis(engine)
    return summary


def collect_videos(
    channels_file: str | None,
    queries_file: str | None,
    videos_per_channel: int = 15,
) -> list[dict]:
    videos: list[dict] = []
    if channels_file:
        videos.extend(
            r
            for r in latest_videos_from_file(
                channels_file,
                n=videos_per_channel,
                include_transcripts=True,
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
    parser.add_argument(
        "--videos-per-channel",
        type=int,
        default=15,
        help="latest long-form videos fetched from each configured channel (max 15)",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--engine",
        choices=ENGINES,
        default="auto",
        help="wiki-writing agent (auto tries Claude, then Codex)",
    )
    parser.add_argument(
        "--refresh-wiki",
        action="store_true",
        help="rewrite the existing wiki into a coherent textbook without retrieving videos",
    )
    parser.add_argument(
        "--enrich-wiki",
        action="store_true",
        help="research and enrich prioritized wiki gaps without retrieving videos",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="maximum research-queue items to complete during enrichment (default: 3)",
    )
    parser.add_argument(
        "--validate-wiki",
        action="store_true",
        help="check scholarly footnote and reference-section integrity",
    )
    parser.add_argument(
        "--freshness-report",
        action="store_true",
        help="write wiki/_freshness-report.md and report missing review metadata",
    )
    parser.add_argument(
        "--audit-wiki",
        action="store_true",
        help="run the monthly stale-evidence, correction, and synthesis audit",
    )
    parser.add_argument("--audit-pages", type=int, default=8, help="maximum pages in a monthly correction audit")
    parser.add_argument("--develop-hypotheses", action="store_true", help="run the bounded weekly hypothesis workshop")
    parser.add_argument("--max-new-hypotheses", type=int, default=1, help="maximum new hypotheses per workshop")
    parser.add_argument("--check-sources", action="store_true", help="rebuild the source registry and check DOI/PubMed retraction status")
    args = parser.parse_args(argv)

    if args.refresh_wiki:
        if args.dry_run:
            print(REFRESH_PROMPT)
            return 0
        print("Refreshing existing wiki into textbook form")
        return 0 if refresh_wiki(args.engine) else 1

    if args.enrich_wiki:
        if args.pages < 1:
            parser.error("--pages must be at least 1")
        prompt = enrichment_prompt(args.pages)
        if args.dry_run:
            print(prompt)
            return 0
        print(f"Enriching up to {args.pages} prioritized wiki pages")
        return 0 if enrich_wiki(args.pages, args.engine) else 1

    if args.validate_wiki:
        errors = validate_wiki()
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("Wiki references, wikilinks, and schema are structurally valid")
        return 0

    if args.freshness_report:
        bootstrap_wiki()
        report, errors = freshness_report()
        (WIKI_DIR / "_freshness-report.md").write_text(report)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("Wiki freshness report written")
        return 0

    if args.audit_wiki:
        if args.audit_pages < 1:
            parser.error("--audit-pages must be at least 1")
        return 0 if audit_wiki(args.engine, dry_run=args.dry_run, pages=args.audit_pages) else 1

    if args.develop_hypotheses:
        if args.max_new_hypotheses < 1:
            parser.error("--max-new-hypotheses must be at least 1")
        return 0 if develop_hypotheses(args.max_new_hypotheses, args.engine, args.dry_run) else 1

    if args.check_sources:
        bootstrap_wiki()
        _, warnings = write_source_registry(check=True)
        if warnings:
            print("\n".join(warnings), file=sys.stderr)
        return 1 if any("retraction" in warning for warning in warnings) else 0

    channels = None if args.queries_only else args.channels_file
    queries = None if args.channels_only else args.queries_file
    videos = collect_videos(
        channels,
        queries,
        videos_per_channel=args.videos_per_channel,
    )
    conn = connect()
    summary = run_pipeline(
        videos,
        conn,
        dry_run=args.dry_run,
        limit=args.limit_videos,
        engine=args.engine,
    )
    print(
        f"\n{summary['new']} new videos; {summary['integrated']} integrated; "
        f"{summary['failed_batches']} failed batches"
    )
    return 1 if summary["failed_batches"] else 0


if __name__ == "__main__":
    sys.exit(main())
