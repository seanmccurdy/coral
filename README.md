<p align="center">
  <img src="wiki/assets/coral-header.png" alt="A sunlit coral reef whose connected, renewing ecosystem inspired Coral" width="100%">
</p>

<h1 align="center">Coral</h1>

<p align="center"><strong>A living, source-aware textbook about health, aging, nutrition, exercise, and the systems that connect them.</strong></p>

Coral is built to do more than collect information. Each chapter defines its subject, explains mechanisms from first principles, distinguishes different strengths of evidence, identifies practical implications and open questions, and connects its topic to the rest of the knowledge system. The aim is a textbook that can keep learning without losing its structure or its memory.

## Why “Coral”?

The name was inspired by John C. Bythell, Barbara E. Brown, and Thomas B. L. Kirkwood’s review, [“Do reef corals age?”](https://doi.org/10.1111/brv.12391), published in *Biological Reviews*.

Coral colonies are made of connected, modular polyps that bud, regenerate, and renew the larger system. Although individual polyps and colonies can accumulate damage and decline, the asexual lineage has been regarded as potentially immortal: its continuity does not require every constituent part to remain unchanged forever.

That possibility captures the question at the heart of Coral: how can a living system preserve itself through maintenance, repair, renewal, and a supportive environment? Human longevity is not simply a matter of keeping every component frozen in time. It emerges from connected biological systems that continually manage damage, replace parts, preserve function, and adapt to stress. This wiki follows that same pattern in miniature—revising individual pages as evidence changes while preserving and strengthening the larger body of knowledge.

## Repository map

```text
coral/
├── README.md                         # project orientation
└── wiki/
    ├── _index.md                     # canonical entry point and writing contract
    ├── changelog.md                  # additions, revisions, and corrections
    ├── _research-queue.md            # prioritized gaps in textbook coverage
    ├── _review-queue.md              # bounded, risk-ranked correction queue
    ├── _freshness-report.md          # evidence-review status by chapter
    ├── _sources.json                 # DOI/PubMed source registry
    ├── _dependencies.json            # reverse links and synthesis dependencies
    ├── concepts/
    │   ├── aging-biology/
    │   ├── brain-and-behavior/
    │   ├── cardiometabolic/
    │   ├── diagnostics-and-screening/
    │   ├── environment-and-society/
    │   ├── exercise-and-movement/
    │   ├── immune-system/
    │   ├── nutrition-and-metabolism/
    │   ├── reproductive-health/
    │   └── skin-and-hair/
    ├── interventions/                # actions, treatments, and protocols
    ├── debates/                      # genuine scientific disagreements
    ├── hypotheses/                   # falsifiable proposals and experimental tests
    ├── people/                       # recurring researchers and frameworks
    └── synthesis/
        ├── aging-model.md             # connected causal model
        └── practice-playbook.md       # evidence-graded actions by cadence
```

Every concept domain contains its own `_index.md` with a suggested reading path. Wikilinks such as `[[cellular-senescence]]` connect chapters across folders, so the directory tree supplies orientation without dividing the subject into isolated silos.

## How to read the wiki

There are three useful ways in:

1. **Learn the whole system.** Begin with the [main index](wiki/_index.md), then read the domain indexes and the [aging model](wiki/synthesis/aging-model.md).
2. **Start with a question.** Open a relevant concept or intervention, follow its related links, and use its “Gaps & open questions” section to see where knowledge ends.
3. **Start with action.** Use the [practice playbook](wiki/synthesis/practice-playbook.md), then follow each recommendation back to the chapters and evidence that justify it.
4. **Explore what might come next.** Visit the [hypothesis lab](wiki/hypotheses/_index.md) for explicitly speculative, testable ideas derived from gaps in the aging model.

The synthesis pages are maps, not substitutes for the terrain. Their recommendations and causal links should always be read alongside the underlying chapters and cited evidence.

The hypothesis lab is not a recommendations section. It develops human-direct ideas about applying, combining, timing, personalizing, measuring, and delivering low-risk health practices more effectively. Proposed tests must be feasible without a wet lab and use human function, symptoms, behavior, clinical state, or quality of life as primary outcomes. Cell, animal, gene-editing, novel-target, and unapproved-compound hypotheses are outside its scope.

A bounded workshop runs weekly after evidence enrichment. It reviews existing hypotheses, generates and ranks three explicitly unreviewed seeds in an idea nursery unless its twelve slots are full, and develops the strongest candidate. It publishes at most one hypothesis per run and is allowed to publish none when the available ideas do not meet the causal, evidentiary, testability, or safety standard.

Every promoted hypothesis includes a Mermaid mechanistic map showing the biological node being leveraged, the proposed causal chain, competing explanations, measurable endpoint levels, and major safety tradeoffs. The map distinguishes supported links from extrapolation and the novel link actually being tested.

## Read it in Obsidian

Coral is written as an [Obsidian](https://obsidian.md/) vault. GitHub works well for browsing individual pages, but Obsidian makes the wiki’s structure much easier to explore: `[[wikilinks]]` become navigable connections, backlinks reveal what depends on a chapter, Mermaid diagrams render inline, and the graph view exposes relationships across domains.

To use it locally:

```bash
git clone https://github.com/seanmccurdy/coral.git
```

Then install Obsidian, choose **Open folder as vault**, and select the cloned `coral/wiki` directory—not the repository root. Start with `_index.md`. To receive future wiki updates, run `git pull` from the cloned `coral` directory.

If you plan to annotate or modify your local copy, use a separate Git branch or keep personal notes outside the tracked files so upstream updates remain easy to merge.

## How Coral works

Coral organizes knowledge around subjects rather than episodes or speakers. A chapter defines its topic, builds the mechanism from first principles, separates established knowledge from inference, distinguishes biomarkers from clinical outcomes, preserves genuine disagreements, states practical implications with their evidence strength, identifies open questions, and connects upstream causes to downstream consequences and interventions. Episodes support that exposition; they do not become its narrative spine.

The system preserves two complementary kinds of attribution:

- **Provenance:** podcast and video citations show where an idea, interpretation, or framework entered the system.
- **Evidence:** papers, guidelines, consensus statements, and official records show what supports the scientific claim itself.

Those roles are not interchangeable. An expert discussion can surface an important idea without proving it; a mechanistic experiment can establish a pathway without demonstrating a human health outcome; and a biomarker can predict risk without being a valid treatment target. Chapters therefore identify the kind of evidence supporting a claim—from guidelines and evidence syntheses through randomized trials, observational and mechanistic human studies, animal and cell work, expert interpretation, and commercial claims. Evidence rank is distinct from topic priority: a foundational subject can remain deeply uncertain, while a lower-level experiment may be the best available evidence for a narrow mechanism.

The textbook is maintained as a revisable system. New material is integrated into existing explanations, priority gaps receive dedicated research, and chapters record when their evidence was reviewed and through what cutoff date. Safety claims, clinical recommendations, contested topics, and chapters used by synthesis receive earlier review. DOI and PubMed records are checked for resolution and retraction signals, while reverse dependencies identify the chapters and synthesis pages that may need reconsideration when a claim changes.

The [scientific-rigor audit](wiki/_scientific-rigor-audit.md) tracks corpus-wide fact-checking, confirmed corrections, and P0/P1/P2 priorities. A chapter marked `review-due` or `under-review` should not be treated as independently verified merely because its prose includes an evidence grade.

Corrections are not silently overwritten. The current conclusion is revised, the reason for the change is recorded, useful historical context is retained, and affected synthesis pages are reconsidered. The [changelog](wiki/changelog.md) provides the ongoing record. In this way, maintenance is part of the textbook itself rather than an invisible process behind it.

## Contributing corrections

If you find an error, unsupported claim, broken reference, retracted source, or outdated recommendation, please open a GitHub issue and include:

- the affected page and passage;
- what appears incorrect or stale;
- the strongest relevant primary source, guideline, or official record;
- whether the correction could affect a practical recommendation or synthesis page.

Focused corrections with direct evidence are more useful than broad requests to “cover” a topic.

## Scope and limitations

Coral is educational and is not medical advice. It cannot account for an individual’s history, diagnoses, medications, contraindications, goals, values, or clinical context. Health decisions should be made with qualified professionals who can evaluate those factors.

The wiki will contain uncertainty and occasional errors. Citation does not guarantee correctness, and absence from the wiki does not imply that a subject is unimportant. The project’s goal is not finality; it is a knowledge structure capable of exposing uncertainty, incorporating correction, and improving over time.

The software, raw transcripts, private data, and local infrastructure used to generate and maintain Coral are intentionally not published in this repository.
