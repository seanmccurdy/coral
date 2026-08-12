---
type: debate
title: Perimenopause assessment and testing
tags: [hormones, longevity, sleep-brain]
updated: 2026-08-11
evidence_reviewed: 2026-08-12
evidence_cutoff: 2026-08-12
review_status: current
review_interval: 180d
---

# Perimenopause assessment and testing

> [!important] Evidence update — 2026-08-12
> The completed review aligned diagnostic testing with the 2024-amended NICE guideline: in people aged 45 or older with a typical presentation, do not use estradiol or other ovarian tests to identify perimenopause or menopause, and reserve FSH confirmation mainly for ages 40–45 with symptoms or suspected ovarian insufficiency under 40. Difficulty interpreting bleeding during hormonal treatment warrants clinical assessment; it does not by itself validate a serum estradiol threshold. This narrows the earlier, source-reported suggestion that estradiol testing after hysterectomy or with a progestin IUD can confirm the transition. ([NICE NG23 recommendations](https://www.nice.org.uk/guidance/ng23/chapter/Recommendations))

Perimenopause is the variable transition before the final menstrual period, during which ovarian hormone patterns and bleeding become less predictable. Menopause is identified retrospectively after twelve months without menstruation when no other cause explains the absence. The central testing problem is that symptoms are real but nonspecific, while fluctuating reproductive hormones make a single apparently normal result poor evidence against perimenopause. Testing is useful when it answers a defined differential-diagnosis or risk-management question, not when it attempts to prove every symptom is hormonal. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))

```mermaid
flowchart TD
  S[Symptoms, cycle change, age, history] --> STAGE{Menstrual history interpretable?}
  STAGE -->|typical transition| CLIN[Clinical assessment]
  STAGE -->|no: hysterectomy, hormonal IUD, irregular baseline, suppression| SEL[Selective hormone testing may clarify context]
  S --> MIMIC[Evaluate plausible mimics and coexisting disease]
  MIMIC --> THY[Thyroid pathway]
  MIMIC --> IRON[CBC and ferritin when indicated]
  MIMIC --> SLEEP[Sleep, mood, medicines, pregnancy, other causes]
  S --> RISK[Independent preventive risk assessment]
  RISK --> CV[Blood pressure, standard lipids; ApoB or Lp(a) when useful]
  RISK --> MET[Validated diabetes screening]
  RISK --> BONE[Fracture risk; DXA by age or risk]
  CLIN --> PLAN[Shared management plan]
  SEL --> PLAN
  THY --> PLAN
  IRON --> PLAN
  SLEEP --> PLAN
  CV --> PLAN
  MET --> PLAN
  BONE --> PLAN
```

## Clinical diagnosis versus hormone confirmation

The source describes perimenopause as a zone of hormonal chaos: estradiol, progesterone, FSH, and LH may move unpredictably, so one blood, saliva, or urine sample can misrepresent the transition. Its strongest position is that a single FSH or estradiol value should not exclude or confirm ordinary perimenopause when age, symptoms, and cycle history already provide the relevant pattern. Selective estradiol testing may help when menstrual history cannot be interpreted—for example after hysterectomy, with amenorrhea from a progestin IUD, or with possible hypothalamic suppression—but assay choice and interpretation remain clinical questions. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))

Mary Claire Haver also describes measuring estradiol in some postmenopausal patients using transdermal therapy to assess variable absorption and bone protection, and measuring testosterone broadly while treating selected women with hypoactive sexual desire disorder. These are practice positions, not universal thresholds: the transcript acknowledges that no testosterone range guarantees libido, and it does not establish an estradiol concentration that proves fracture protection. Symptoms, indication, safety, and validated monitoring guidance matter more than optimizing a number. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc)) [[proactive-health-monitoring]]

## Tests for mimics and consequences

Fatigue, cognitive slowing, sleep disturbance, weight change, hair loss, palpitations, and mood symptoms overlap with thyroid disease, iron deficiency, psychiatric illness, medication effects, and sleep disorders. Haver recommends TSH plus free T4 and sometimes free T3, arguing that TSH alone can miss disease. The contested boundary is universal expansion: TSH reflects the pituitary-thyroid feedback loop, and the transcript presents no diagnostic-yield or outcome data showing that free T3 and free T4 should be ordered for every symptomatic menopausal patient. Additional testing is best directed by symptoms, examination, pituitary context, medicines, and the initial result. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))

Heavy or irregular bleeding can deplete iron stores before hemoglobin falls. Ferritin therefore answers a different question from a CBC or serum iron and can help explain fatigue, exercise intolerance, restless legs, cognitive slowing, or hair shedding. Low ferritin should trigger assessment of bleeding and other causes, not merely replacement. Oral and intravenous iron differ in speed, gastrointestinal burden, cost, and indication; the source's preference for infusion when stores are critically low is not a universal protocol and requires clinician-directed diagnosis and follow-up. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc)) Heavy bleeding also has structural causes that a hormone-focused work-up can miss: adenomyosis (endometrial-like tissue within the uterine muscle, prevalence estimated at 20–30% of women and classically presenting in the forties) and submucosal fibroids both cause heavy, anemia-producing bleeding and warrant imaging by an operator attentive to the myometrium and junctional zone. [[adenomyosis]] (Peter Attia MD — "397 - Endometriosis and adenomyosis: diagnosis, fertility, reproductive aging, & emerging treatments", 2026-06-22, [link](https://www.youtube.com/watch?v=IxHRYDM64dQ))

The stakes of the testing question rise when cognition is the presenting symptom. Estrogen loss can produce objective memory, executive, and word-finding deficits indistinguishable from early Alzheimer's disease, and patients have carried dementia misdiagnoses whose impairment resolved with hormone replacement or targeted retraining; conversely, estrogen deficiency with a normal FSH and LH has been observed in a young woman with disabling brain fog, so gonadotropins alone cannot exclude a hormonal cause. This supports selective estradiol testing—and explicit consideration of reproductive stage—whenever a woman in her 40s or 50s is being evaluated for possible dementia, a narrower and stronger indication than routine hormone panels for ordinary transition symptoms. [[menopause-related-cognitive-impairment]] (Peter Attia MD — "399 - The evolution of Alzheimer's disease and dementia care | Gayatri Devi, M.D.", 2026-07-13, [link](https://www.youtube.com/watch?v=x7NhqMOwdOM))

High-sensitivity C-reactive protein is a nonspecific inflammatory marker. Haver proposes it as an optional measure of low-grade inflammation after estrogen decline but also acknowledges that it cannot locate a cause. It is therefore unsuitable for diagnosing menopause or attributing inflammation to estrogen withdrawal; infection, adiposity, autoimmune disease, smoking, injury, and other contexts can change it. Testing is defensible when it changes cardiovascular risk assessment or a defined work-up, not as a general inflammation score. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc)) [[inflammaging-and-il-6]]

## Cardiometabolic risk

Menopause can coincide with less favorable body composition, insulin sensitivity, and lipoprotein patterns, but assessment should distinguish reproductive stage, aging, and baseline risk. ApoB estimates atherogenic-particle number, while lipoprotein(a), or Lp(a), is substantially inherited and can reveal risk not apparent from LDL cholesterol alone. Haver recommends both and describes small dense LDL as a possible emerging marker of perimenopause. ApoB and Lp(a) can refine cardiovascular risk; the transcript does not establish small dense LDL as a validated diagnostic test for perimenopause. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc)) [[nmr-blood-analysis]]

Fasting glucose and hemoglobin A1c detect different aspects of dysglycemia, while fasting insulin can reveal compensatory hyperinsulinemia. HOMA-IR combines fasting glucose and insulin, but assay variability and population-dependent thresholds limit one universal cutoff. Haver's claims that a value above two establishes insulin resistance and that risk doubles or triples across menopause lack study detail in the transcript. Fasting insulin or HOMA-IR should supplement—not replace—validated diabetes screening, blood pressure, lipids, body-composition context, and longitudinal change. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc)) [[visceral-and-ectopic-fat]]

## Bone density and vitamin D

Estrogen restrains bone resorption; its loss shifts remodeling toward net loss, making the transition relevant to later osteoporosis and fracture. Haver favors DXA substantially earlier than age 65 and cites rapid loss around the transition. The disagreement is between universal early baseline testing and risk-directed screening: an earlier scan can reveal low density, but adds cost and may not change management in a low-risk person. Age, prior fragility fracture, low body weight, glucocorticoid exposure, smoking, family history, and other validated factors should determine whether earlier DXA is likely to help. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))

Vitamin D supports calcium and bone physiology, and deficiency should be corrected. Haver reports frequent low values in her clinic, uses time-limited prescription dosing with remeasurement, and targets 60–100 while describing up to 4,000 IU/day as safe. The transcript does not demonstrate that 60–100 improves fractures relative to conventional sufficiency ranges, and a tolerable upper intake level is not a universal treatment dose. Supplement intensity and recheck cadence should follow the measured level, intake, malabsorption risk, kidney and calcium context, and clinical guidance; prolonged high dosing can cause toxicity. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc)) [[supplement-evidence-and-safety]]

## Practical implications

- **At a routine visit during the transition: document menstrual change, vasomotor and genitourinary symptoms, sleep, mood, cognition, medicines, pregnancy possibility, and functional impact — strong clinical-assessment principle.** Do not use one normal FSH or estradiol result to dismiss a compatible pattern. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))
- **When bleeding is heavy or fatigue, restless legs, exercise intolerance, or hair shedding is present: discuss CBC and ferritin and evaluate the bleeding source — moderate-to-strong.** Treat documented deficiency with an oral or intravenous plan matched to severity and tolerance, then recheck as directed. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))
- **At preventive-care cadence: assess cardiovascular and diabetes risk with validated measures; consider ApoB and at least once Lp(a) when they refine management — moderate-to-strong.** Do not use small dense LDL, fasting insulin, or HOMA-IR alone to diagnose perimenopause or diabetes. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))
- **At the individual's age or risk threshold: estimate fracture risk and obtain DXA when it can change management — strong for risk-directed screening, contested for universal early scanning.** Continue safe resistance and impact exercise, adequate nutrition, smoking avoidance, and fall-risk reduction. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))
- **Before vitamin D or hormone treatment: define the indication, contraindications, target outcome, monitoring plan, and stopping rule — strong safety principle.** Do not chase a clinic-specific vitamin D, estradiol, or testosterone target without outcome evidence. (@drmaryclaire (Dr. Mary Claire Haver, MD) — "Menopause Masterclass: When 'Normal Labs' Are Lying to You", 2026-07-28, [link](https://www.youtube.com/watch?v=c8jUaFBCudc))

## Gaps & open questions

- Which compact test set improves patient-important outcomes beyond history and ordinary preventive care during perimenopause?
- When do repeated estradiol or FSH measurements change management when menstrual history is unavailable?
- Does universal early baseline DXA reduce fractures enough to outweigh cost and treatment burden?
- Which fasting-insulin assay and HOMA-IR thresholds predict outcomes across diverse populations?
- Does small dense LDL add useful information beyond cycle history, ApoB, non-HDL cholesterol, and overall risk?
- What vitamin D range optimizes fracture outcomes without encouraging unnecessary high-dose treatment?
- Which symptomatic patients with normal TSH benefit from additional thyroid tests?

## Related

[[adhd-and-reproductive-hormone-transitions]] · [[menopause-related-cognitive-impairment]] · [[menopause-hormone-therapy]] · [[ovarian-aging-and-tissue-cryopreservation]] · [[jennifer-pearlman]] · [[adenomyosis]] · [[endometriosis]] · [[oocyte-aneuploidy-and-reproductive-aging]] · [[proactive-health-monitoring]] · [[nmr-blood-analysis]] · [[visceral-and-ectopic-fat]] · [[inflammaging-and-il-6]] · [[supplement-evidence-and-safety]] · [[cognitive-reserve-and-brain-health]] · [[practice-playbook]] · [[aging-model]]
