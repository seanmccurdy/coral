---
type: concept
title: NMR lipoprotein analysis
tags: [longevity]
updated: 2026-08-10
---

# NMR lipoprotein analysis

Clinical blood analysis by proton NMR spectroscopy, invented by
[[jim-otvos]]. A single low-tech ~30-second NMR spectrum of plasma is
deconvolved by computer into the signals of VLDL, LDL, and HDL particles
and their size subclasses, yielding particle concentrations — the basis
of the NMR LipoProfile (LDL-P) test and later composite scores
([[lpir-score]], [[glyca]], [[mvx]]) (Peter Attia MD — "402 ‒ NMR blood
analysis: how mortality risk and more can be assessed from a single blood
sample", 2026-08-03, [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).

## How it works

- The methyl groups of lipids carried in lipoproteins give a composite
  NMR signal. The same lipids in different-sized packages resonate at
  slightly but very reproducibly different frequencies — larger particles
  slightly lower, smaller slightly higher — so a deconvolution model can
  work backwards from the composite signal shape to the concentrations of
  each particle class and size subclass (Peter Attia MD — "402 ‒ NMR
  blood analysis: how mortality risk and more can be assessed from a
  single blood sample", 2026-08-03,
  [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).
- Because the signal reflects particles rather than their variable
  cholesterol/triglyceride cargo, results are reported as particle
  concentrations in nmol/L, not mg/dL (Peter Attia MD — "402 ‒ NMR blood
  analysis: how mortality risk and more can be assessed from a single
  blood sample", 2026-08-03,
  [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).
- Machine learning applied to the spectrum can additionally produce an
  accurate extended lipid panel including ApoB (FDA-cleared quality) at
  no incremental analytic cost (Peter Attia MD — "402 ‒ NMR blood
  analysis: how mortality risk and more can be assessed from a single
  blood sample", 2026-08-03,
  [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).
- Contrast with standard lipid panels: enzymatic/colorimetric assays
  measure cholesterol and triglyceride mass, and LDL-C is usually
  *calculated* (classically Friedewald's triglycerides÷5 estimate of
  VLDL-C; newer NIH equations used by LabCorp improve on it) (Peter Attia
  MD — "402 ‒ NMR blood analysis: how mortality risk and more can be
  assessed from a single blood sample", 2026-08-03,
  [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).

## Origin story

The field began with a 1986 New England Journal of Medicine paper
claiming NMR line-width of plasma could diagnose cancer. Otvos showed the
"cancer signal" was a lipoprotein signal — narrowing driven by the high
triglycerides and low HDL cholesterol common in cancer patients — and
then repurposed the composite signal as a quantitative lipoprotein assay,
validating small-vs-large LDL measurement against Ron Krauss's gradient
gel electrophoresis (Peter Attia MD — "402 ‒ NMR blood analysis: how
mortality risk and more can be assessed from a single blood sample",
2026-08-03, [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).

## Commercialization and its fragility

- LipoScience (founded mid-1990s) built the Vantera NMR analyzer — the
  only clinical NMR analyzer in the world — FDA-cleared with LDL-P in
  2011; machines cost ~$400–500k but have no per-assay consumables, so
  high-volume tests cost on the order of $1 (Peter Attia MD — "402 ‒ NMR
  blood analysis: how mortality risk and more can be assessed from a
  single blood sample", 2026-08-03,
  [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).
- LabCorp acquired LipoScience in 2014 for financial reasons, recalled
  analyzers placed at Mayo, Cleveland Clinic, Scripps, and ARUP, and did
  not continue the in-vitro-diagnostics vision or market the science —
  Otvos warns the aging first-generation analyzers will eventually fail,
  and continuation depends on an IVD company licensing the technology
  (Peter Attia MD — "402 ‒ NMR blood analysis: how mortality risk and
  more can be assessed from a single blood sample", 2026-08-03,
  [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).
- A structural obstacle: US reimbursement pays per named test, so
  analytically "free" added information (LPIR, GlycA, MVX ride along on
  the same 150 µL spectrum) is commercially disincentivized (Peter Attia
  MD — "402 ‒ NMR blood analysis: how mortality risk and more can be
  assessed from a single blood sample", 2026-08-03,
  [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).

## Known limitation

Under extreme CETP inhibition (e.g. obicetrapib in the Broadway/Brooklyn
trials), very large cholesterol-rich HDL particles approach small-LDL
size and the deconvolution can misallocate them; the older algorithm
overstated LDL-P reductions relative to ApoB, and reanalysis with the
current model brings them in line (Peter Attia MD — "402 ‒ NMR blood
analysis: how mortality risk and more can be assessed from a single blood
sample", 2026-08-03, [link](https://www.youtube.com/watch?v=IMbghqZ1iXI)).

## Related

- [[jim-otvos]]
- [[ldl-particle-number]]
- [[ldl-particle-size]]
- [[lpir-score]]
- [[glyca]]
- [[mvx]]
