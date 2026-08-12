---
type: concept
title: Biological age biomarkers
tags: [longevity]
updated: 2026-08-11
evidence_reviewed: never
evidence_cutoff: unknown
review_status: review-due
review_interval: 365d
---

# Biological age biomarkers

Biological-age biomarkers compress molecular or clinical measurements into an estimate of accumulated state, pace of change, or mortality risk. These are different targets. DunedinPACE, for example, is calibrated like a speedometer around 1.0 biological year per chronological year; an age clock instead estimates a state relative to reference ages. (@ABCNewsIndepth (ABC News In-depth) — "The health trends outpacing regulation and putting people at risk | Four Corners Documentary", 2026-07-20, [link](https://www.youtube.com/watch?v=77TTDkR3nbI))

```mermaid
flowchart LR
  S[Blood or tissue sample] --> F[Molecular features]
  F --> M[Trained model]
  M --> O[Age, pace, or risk score]
  O --> R[Repeat after intervention]
  R -. only if validated .-> C[Clinical benefit inference]
```

## Interpretation and evidence

DNA methylation clocks select patterns across hundreds of CpG sites, but different clocks answer different questions. First-generation clocks were optimized to predict chronological age; PhenoAge and GrimAge incorporate methylation proxies for clinical phenotypes, inflammatory proteins, and smoking exposure; DunedinPACE estimates a longitudinally trained rate of physiological change. GrimAge has been the strongest mortality predictor in large comparisons described in the source, while DunedinPACE can be more responsive to weight loss because body-mass change contributed to its training target. Disagreement is therefore expected and is not resolved by choosing whichever score improved. (@FoundMyFitness (FoundMyFitness) — "The 7 Habits of People Who Age Slower | Dr. Steve Horvath", 2026-06-10, [link](https://www.youtube.com/watch?v=3pRiY2zHt8c))

Clocks trained for different outcomes can disagree because they measure different feature sets and optimize different targets. Their research value is the possibility of detecting directional change over 3–12 months instead of waiting decades for disease or death, but that convenience creates a surrogate-endpoint problem: an intervention may move a clock without improving health. Conventional blood pressure, lipids, glucose, kidney function, fitness, and body composition remain directly interpretable risk measures; richer interpretation of routine data may add more preventive value than an unvalidated consumer age number. (@ABCNewsIndepth (ABC News In-depth) — "The health trends outpacing regulation and putting people at risk | Four Corners Documentary", 2026-07-20, [link](https://www.youtube.com/watch?v=77TTDkR3nbI))

Predictive validity is not surrogate validity. A clock can predict mortality without proving that an intervention-induced change predicts an intervention-induced change in mortality. Horvath considers the convergence with beneficial interventions increasingly encouraging, but explicitly notes that methylation clocks have not met the regulatory standard for an accepted surrogate endpoint. Trials should report several prespecified clocks plus functional and clinical measures; principal-component versions can have technical repeatability on the order of months, making small personal changes difficult to distinguish from noise. (@FoundMyFitness (FoundMyFitness) — "The 7 Habits of People Who Age Slower | Dr. Steve Horvath", 2026-06-10, [link](https://www.youtube.com/watch?v=3pRiY2zHt8c))

Intervention evidence follows baseline burden and endpoint choice. Antiretroviral treatment in people with HIV and anti-TNF treatment in inflammatory disease produce comparatively large clock improvements alongside treatment of major pathology. Caloric restriction produced a small DunedinPACE signal without GrimAge or PhenoAge changes in a trial with limited adherence; a semaglutide preprint in obesity reportedly moved multiple clocks after substantial weight loss. Omega-3, multivitamin, vitamin D, and exercise trials generally show smaller, clock-dependent changes measured in months, not proof of years of added life. The claim that small short-term clock changes compound linearly for decades is plausible speculation, not demonstrated longitudinal evidence. (@FoundMyFitness (FoundMyFitness) — "The 7 Habits of People Who Age Slower | Dr. Steve Horvath", 2026-06-10, [link](https://www.youtube.com/watch?v=3pRiY2zHt8c))

Observational methylation associations support prioritizing smoking avoidance, healthy weight, vegetables, physical activity, and social connection, but they do not rank causal effect sizes. Horvath highlighted a strong vegetable-intake correlation and a newer association between cumulative social advantage and lower GrimAge; both can reflect correlated behaviors and social conditions. Reports of inherited effects from parental or grandparental stress remain substantially contested, whereas severe personal chronic stress has more support and ordinary short-term deadline stress appears weakly related to clock age. (@FoundMyFitness (FoundMyFitness) — "The 7 Habits of People Who Age Slower | Dr. Steve Horvath", 2026-06-10, [link](https://www.youtube.com/watch?v=3pRiY2zHt8c))

Mortality-risk scores are not necessarily biological-age measures. [[nmr-blood-analysis|MVX]] combines inflammatory and metabolic-malnutrition spectral features and reportedly predicts mortality with little association to chronological age, including in a described young-adult cohort. Its proponent, James Otvos, interprets it as metabolic vulnerability—the capacity to survive whatever disease or stress occurs—rather than the rate of acquiring a particular disease. This is a distinctive, observationally supported hypothesis; it is not evidence that MVX measures aging, causes death, or is a validated treatment target. (@PeterAttiaMD (Peter Attia MD) — "402 ‒ NMR blood analysis: how mortality risk and more can be assessed from a single blood sample", 2026-08-03, [link](https://www.youtube.com/watch?v=IMbghqZ1iXI))

LinAge illustrates a second kind of relabeling: clinical chemistry, health-history, and lifestyle inputs estimate ten-year mortality risk and then express that risk as the chronological age with an equivalent model prediction. A lower age-equivalent score can be directionally coherent with improved ApoB, insulin-related markers, and body composition, but it is not a direct measurement of tissue age or proof that mortality risk actually changed by the displayed number of years. Kaeberlein considers LinAge 2 more clinically useful than many consumer clocks because its components and risk interpretation are more actionable; this is his expert preference, and the transcript provides one uncontrolled example rather than comparative validation. (@matt.kaeberlein (Healthspan Medicine) — "Optispan Success Story: What 18 Months of Real Biomarker Data Actually Looks Like with Carlos Pinto", 2026-03-01, [link](https://www.youtube.com/watch?v=qlv8Q-CHWcc))

## Practical implications

Use established clinical risk factors at guideline-recommended intervals. If using a biological-age test, obtain the same laboratory platform and a prespecified panel including both state/risk and pace measures, repeat only after a meaningful intervention interval measured in months, and demand changes larger than technical error. Interpret results alongside function and conventional outcomes, and do not use a single score to justify supplements or unapproved treatments. Evidence for clocks as cohort and trial measures is moderate; evidence that consumer-guided clock optimization improves health is absent. (@ABCNewsIndepth (ABC News In-depth) — "The health trends outpacing regulation and putting people at risk | Four Corners Documentary", 2026-07-20, [link](https://www.youtube.com/watch?v=77TTDkR3nbI)) (@FoundMyFitness (FoundMyFitness) — "The 7 Habits of People Who Age Slower | Dr. Steve Horvath", 2026-06-10, [link](https://www.youtube.com/watch?v=3pRiY2zHt8c))

## Gaps & open questions

- Which clocks are causal surrogates rather than correlates?
- What change exceeds technical and day-to-day biological variation?
- Do score-guided interventions improve morbidity or mortality?
- How much of a blood-clock change is altered immune-cell composition rather than within-cell aging?
- Do small supplement-associated changes persist, accumulate, plateau, or disappear over decades?
- Does intervention-induced change in LinAge predict intervention-induced morbidity or mortality beyond the component clinical risk factors?

## Related

[[nmr-blood-analysis]] · [[biological-age-reversal]] · [[immune-aging-and-rejuvenation]] · [[longevity-clinics-and-evidence]] · [[practice-playbook]]
