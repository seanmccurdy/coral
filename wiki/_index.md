# Coral Wiki

A living knowledge base built from video transcripts. Organized by entity
type; domains (longevity, nutrition, fitness, hormones, sleep-brain,
skincare, urbanism) live in each page's `tags` frontmatter.

## Sections

- `concepts/` — mechanisms & ideas (e.g. vo2-max, autophagy)
- `interventions/` — things you can do or take (e.g. rapamycin, creatine, hrt)
- `people/` — researchers & recurring voices (e.g. peter-attia)
- `debates/` — live disagreements (e.g. seed-oils)
- `hypotheses/` — mechanistic, falsifiable proposals for slowing aging; speculation is labeled and kept separate from practical guidance
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

- Frontmatter: `type` (concept | intervention | person | debate | hypothesis | synthesis), `title`, `tags` (domains), `updated` (YYYY-MM-DD).
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
- **Hypothesis development**: the lab develops human-direct hypotheses about low-risk behavior, exercise, nutrition, sleep, adherence, timing, measurement, prevention, and care delivery. Promote an open question only when it has discriminating predictions and can be tested through a feasible human N-of-1, pragmatic, crossover, cohort, or secondary-data design without a wet lab. Cell-, animal-, novel-target-, gene-editing-, and unapproved-compound hypotheses are out of scope. A primary endpoint must measure human function, symptoms, behavior, clinical state, or quality of life—not a biomarker alone. Keep speculation out of the practice playbook. Each hypothesis states its rationale, alternatives, experiment, endpoints, failure criteria, confounders, safety boundary, and status; negative evidence revises or retires it. A Mermaid mechanistic model must show the leveraged node, proposed causal chain, competing pathway, measured endpoints, and important harm branch, with links labeled by evidence strength.
- **Practical implications**: each concept/intervention page states what a
  person should actually do with this knowledge (and at what cadence),
  with the strength of evidence behind it.
- **Unique perspectives**: contrarian or minority takes are captured and
  attributed to their proponent, not averaged into consensus.
- Conflicting claims are recorded as disagreements (prefer a debates/
  page), never silently overwritten.
- Formatting: do not hard-wrap prose — write each paragraph as one line
  and let the reader's editor (Obsidian) soft-wrap. Never reflow existing
  text just to change its width.

## Notable pages

(maintained by the integration agent as pages are added)

- [[aging-model]] — causal map connecting damage, maintenance, cell state, immunity, disease, and interventions
- [[practice-playbook]] — evidence-graded actions by cadence
- [[advanced-glycation-end-products]] — formation, consequences, and repair limits of AGEs
- [[biological-age-biomarkers]] — age, pace, and risk measures and their interpretation
- [[experimental-peptides]] — evidence, compounding, and product-quality risks
- [[pcsk9-inhibition]] — LDL-receptor recycling, lipid lowering, and outcome evidence
- [[biological-age-reversal]] — debate over molecular, biomarker, functional, and organism-level reversal
- [[longevity-clinics-and-evidence]] — regulatory availability versus clinical evidence
- [[nmr-blood-analysis]] — spectral lipoprotein, insulin-resistance, inflammation, and mortality-risk measurement
- [[environmental-pollution-and-health]] — cumulative exposure, causal inference, and risk-prioritized mitigation
- [[cognitive-reserve-and-brain-health]] — maintenance, reserve, modifiable risks, and cognitive function across aging
- [[supplement-evidence-and-safety]] — outcome-centered evaluation, interactions, dosing, and evidence tiers
- [[ketogenic-diet-apob-and-atherosclerosis]] — whether metabolic health modifies risk from diet-induced ApoB
- [[omega-3-fatty-acids]] — DHA/EPA mechanisms, cognitive evidence, dosing, product quality, and atrial-fibrillation risk
- [[visceral-and-ectopic-fat]] — fat distribution, measurement, diet, exercise, sleep, and metabolic risk
- [[nutrition-evidence-and-personalization]] — food matrices, substitutions, time scale, applicability, and dietary patterns
- [[performance-nutrition-and-hydration]] — carbohydrate, protein, fluid, electrolytes, GI tolerance, and recomposition
- [[trunk-training]] — flexion, rotation, stabilization functions, loading, and weekly programming
- [[youth-resistance-training]] — physical, cognitive, psychosocial, and lifecourse effects of strength work in children
- [[aging-dynamics-and-resilience]] — longitudinal drift, stress response, recovery, physiological noise, and intervention levels
- [[ai-guided-therapeutic-design]] — target selection, antibody generation, filtering, experimental validation, and translation
- [[stress-threat-discrimination]] — learned appraisal of effort versus danger and prediction-error updating
- [[protective-threat-responses]] — fight, flight, freeze, and the less-settled fawn category
- [[social-evaluative-threat-and-criticism]] — how criticism couples task information to acceptance and status threat
- [[skin-barrier-and-moisturization]] — epidermal water balance, barrier disruption, and function-based moisturization
- [[skincare-evidence-and-routine-design]] — formulation, layering, irritation load, marketing claims, and product value
- [[hair-loss-diagnosis-and-scalp-health]] — diagnosis-first treatment, follicle preservation, cleansing, and evidence tiers
- [[topical-retinoids]] — vitamin-A activation, acne and photoaging effects, pigment, and delayed irritation
- [[photoprotection]] — real-world sunscreen film, reapplication, long-wear claims, and garment care
- [[procedural-skin-remodeling]] — IPL, microneedling, radiofrequency, striae, and botulinum-toxin aftercare
- [[dr-dray]] — dermatologist emphasizing diagnosis, routine simplicity, tolerability, and evidence over prestige
- [[erectile-dysfunction-and-vascular-health]] — erectile physiology, vascular sentinel value, apolipoproteins, and cause-directed assessment
- [[male-contraception]] — established and investigational transport-blocking, hormonal, and sperm-specific methods
- [[male-fertility-and-exogenous-testosterone]] — reproductive-axis feedback, testosterone suppression of spermatogenesis, and fertility-preserving decisions
- [[colorectal-cancer-prevention-and-screening]] — polyp progression, dietary pathways, and prevention versus detection strategies
- [[resistant-starch]] — colonic delivery, formulation-specific dosing, and visceral-fat evidence
- [[olive-oil-and-cognitive-aging]] — barrier, connectivity, cognition, and dementia-outcome evidence
- [[creatine-for-depression]] — mixed trials, candidate responders, and microbiome-component uncertainty
- [[microbiome-directed-cancer-therapy]] — early adjunctive trials, immune pathways, and limits of dietary extrapolation
- [[inflammaging-and-il-6]] — context-dependent cytokine signaling, cardiovascular trials, host defense, and exercise adaptation
- [[ezetimibe]] — intestinal cholesterol absorption, secondary-prevention outcomes, lifetime exposure, and the primary-prevention boundary
- [[immune-aging-and-rejuvenation]] — repertoire loss, chronic stimulation, inflammatory feedback, measurement, and experimental renewal
- [[daily-movement-mobility-and-pain]] — distributed activity, usable range, pain triage, graded loading, and movement snacks
- [[human-centered-ai-and-learning]] — learned representations, active tutoring, spatial intelligence, agency, and governance
- [[neuromodulators-and-state-control]] — baseline state, dopamine, catecholamines, acetylcholine, serotonin, and evidence boundaries
- [[immune-recognition-and-trafficking]] — contextual sensing, lymphatic movement, tissue immunity, activation thresholds, and clinical tuning
- [[evolutionary-mismatch-and-weight-regulation]] — evolved appetite, energy storage, modern food environments, and weight-regain pressure
- [[dietary-fiber]] — viscosity, satiety, fermentation, stool bulk, food sources, targets, and tolerance
- [[free-sugars-and-glycemic-response]] — food structure, free versus intrinsic sugar, glucose dynamics, labels, and post-meal activity
- [[mental-strength-and-behavioral-skills]] — thought–emotion–behavior loops, rumination, graded discomfort, digital boundaries, and evidence limits
- [[proactive-health-monitoring]] — risk-directed testing, biomarker interpretation, early sentinels, hormones, and overdiagnosis
- [[energy-balance-and-calorie-counting]] — conservation, measurement error, food quality, timing, and dynamic weight change
- [[probiotics-prebiotics-and-postbiotics]] — category definitions, cancer-association limits, and product-specific weight-maintenance evidence
- [[strength-transfer-and-exercise-specificity]] — general force capacity, sport skill, exercise selection, and contested functional-training claims
- [[automation-employment-and-population]] — task substitution, labor scarcity, new demand, distribution, and demographic decline
- [[durable-well-being-and-hedonic-adaptation]] — reference points, satiation, mastery, relationships, meaning, and evidence limits
- [[self-schema-updating-after-achievement]] — persistent self-beliefs, corrective evidence, self-talk, and achievement integration
- [[training-frequency-and-hypertrophy]] — volume distribution, recovery, repeated-bout adaptation, specialization, and connective-tissue limits
- [[tendon-adaptation-and-rehabilitation]] — tendon load capacity, isometrics, graded loading, pain monitoring, and evidence limits
- [[satiety-oriented-diet-design]] — energy density, protein, fiber, food structure, attention, cues, and adherence
- [[abdominal-definition-and-training]] — muscle development, overlying fat, flexion mechanics, meal structure, hydration, and adjunct evidence
- [[lunge-biomechanics-and-programming]] — step direction, loading rate, stance, trunk angle, load position, and depth
- [[arm-hypertrophy-specialization]] — distributed volume, joint actions, progression, eccentric loading, recovery, and measurement limits
- [[hip-mobility-and-adductor-loading]] — hip opening, FABER screening, active adductor exposure, and test–retest limits
- [[shoulder-force-couples-and-exercise-selection]] — cuff centering, scapular control, position-specific loading, and rehabilitation decisions
- [[sedentary-posture-and-reverse-plank]] — posture interpretation, whole-body extension practice, acute activation, and evidence limits
- [[adhd-and-reproductive-hormone-transitions]] — compensation, hormonal modulation, emotional regulation, differential diagnosis, and layered support
- [[perimenopause-assessment-and-testing]] — clinical staging, selective labs, cardiometabolic and bone risk, and contested screening boundaries
- [[mineral-and-organic-sunscreens]] — finished-film protection, toxicological dose, systemic absorption, and reef-risk disputes
- [[topical-pdrn-and-centella]] — route-specific evidence, standardization, delivery uncertainty, and co-active attribution
- [[elite-endurance-development]] — coupled physiology, technique, tactics, intensity distribution, and long-term development
- [[addiction-recovery-and-emotional-sobriety]] — relief learning, stabilization, continuing care, relapse, exercise, and treatment quality
- [[myth-moral-injury-and-homecoming]] — narrative moral simulation, surrender, repair, shared norms, and institutional restraint
- [[intercity-travel-generalized-cost]] — door-to-door time, usable time, reliability, access, and corridor investment
- [[transit-capacity-and-service-design]] — throughput, dwell, wayfinding, right-of-way, delivered service, and accountability
- [[safe-streets-and-pedestrian-risk]] — systemic crash risk, urban form, disparities, jurisdiction, and safety-first design
- [[alzheimers-spectrum-and-diagnosis]] — dementia spectrum, comorbid pathology, compensation-resistant testing, biomarkers, and sex differences
- [[alzheimers-diagnosis-biological-vs-clinical]] — amyloid-only versus amyloid-plus-tau-plus-symptoms diagnostic criteria and asymptomatic screening
- [[anti-amyloid-immunotherapy]] — monoclonal amyloid clearance, ARIA mechanism, slow titration, cost, and the early-treatment hypothesis
- [[lewy-body-disease-and-synucleinopathies]] — alpha-synuclein spectrum, skin-biopsy diagnosis, dopaminergic misdiagnosis harm, and prognosis
- [[menopause-related-cognitive-impairment]] — estrogen-deficiency cognitive dysfunction, Alzheimer's mimicry, hormonal and non-hormonal treatment
- [[gayatri-devi]] — memory-disorder neurologist emphasizing spectrum framing, domain staging, and slow-titration immunotherapy
- [[muscle-strength-and-mortality]] — strength and mass as mortality predictors, causality, metabolic and reservoir roles, and the aging trajectory
- [[resistance-training]] — progressive overload, intensity, contraction phases, power, recovery signals, and population-specific programming
- [[creatine]] — phosphocreatine mechanism and strength, power, and mass evidence
- [[peter-attia]] — longevity physician emphasizing marginal-decade backcasting, functional metrics, and training de-risking
- [[endometriosis]] — retrograde menstruation, immune clearance failure, hormonal self-sufficiency, imaging-based diagnosis, and chronic management
- [[adenomyosis]] — junctional-zone injury, myometrial invasion, heavy bleeding, and pre-transfer hormonal suppression
- [[oocyte-aneuploidy-and-reproductive-aging]] — the exponential aneuploidy curve, IVF funnel, egg-freezing economics, and rejuvenation claims
- [[breast-cancer-screening]] — risk assessment, modality hierarchy, annual-versus-biennial evidence, and starting-age personalization
- [[brain-cholesterol-homeostasis]] — the sealed brain cholesterol economy, ApoE lipoproteins, sterol biomarkers, and Alzheimer's pharmacology
- [[seed-oils]] — whether hexane extraction and industrial refining make seed oils harmful, versus the linoleic-acid-quantity question
- [[dietary-fat-quality-and-cardiovascular-risk]] — fat chemistry, substitution trials, ApoB pathways, frying oxidation, and evidence synthesis
- [[cardiorespiratory-fitness]] — VO2 max, oxygen delivery, lactate thresholds, and volume–intensity programming
- [[lipoprotein-retention-and-atherogenesis]] — cumulative ApoB exposure, arterial retention, plaque formation, and dietary substitution
- [[layne-norton]] — nutrition researcher emphasizing substitution logic, symmetric confounder handling, and evidence convergence
- [[womens-exercise-across-the-lifespan]] — stable training principles with stage-specific bone, cycle, pregnancy, perimenopause, and later-life constraints
- [[low-energy-availability-and-menstrual-function]] — under-fueling, reproductive-axis conservation, menstrual signals, bone accrual, and GLP-1 overlap
- [[time-efficient-concurrent-training]] — allocating resistance, intervals, and aerobic base within a small weekly time budget
- [[abbie-smith-ryan]] — exercise physiologist emphasizing female-specific measurement without replacing general training science
- [[multi-cancer-early-detection]] — methylated-DNA detection, predictive values, stage-shift evidence, and screening harms
- [[longevity-intervention-prioritization]] — ranking current evidence, expected benefit, harm, burden, and speculative upside
- [[menopause-hormone-therapy]] — indication, formulation, route, endometrial protection, testosterone, and evidence boundaries
- [[ovarian-aging-and-tissue-cryopreservation]] — ovarian endocrine aging, established fertility preservation, and speculative menopause delay
- [[jennifer-pearlman]] — menopause physician emphasizing female-specific aging, individualized hormones, and hybrid care
- [[coronary-ct-angiography]] — contrast coronary anatomy, plaque phenotype, acquisition, serial measurement, and evidence limits
- [[coronary-cta-screening-asymptomatic]] — whether earlier anatomical detection justifies broad screening and repeat imaging
- [[whi-and-menopause-hormone-therapy]] — how population, formulation, route, timing, and outcome limit generalization from the WHI
- [[combat-sports-as-controlled-stress-training]] — bounded physical threat, capability updating, transfer limits, and contact risk
- [[nattokinase]] — fibrinolysis, blood pressure, plaque evidence, bleeding tradeoffs, and absent outcome trials
- [[pre-sleep-routines-and-stimulus-control]] — behavioral conditioning, screen displacement, evening light, and reading-trial limits
- [[microplastics-exposure-and-measurement]] — exposure estimates, analytical false positives, dose, human evidence, and proportionate precautions
- [[statins-and-glycemic-risk]] — cardiovascular outcome benefit, heterogeneous glucose effects, monitoring, and therapy substitution
- [[food-patterns-and-gut-ecology]] — fermented foods, microbial substrates, bowel function, tolerance, and symptom matching
- [[sleep-quality-and-circadian-alignment]] — continuity, architecture, circadian timing, chronotype, and cardiometabolic recovery
- [[food-label-literacy-and-health-halos]] — regulated composition data, marketing cues, repeated exposures, and substitution decisions
- [[pre-sleep-protein-feeding]] — overnight amino-acid availability, total-protein hierarchy, metabolic context, and sleep tradeoffs
- [[breathing-mechanics-and-state-regulation]] — diaphragm and rib mechanics, accessory recruitment, paced breathing, and evidence boundaries
- [[exercise-program-design]] — outcome-first selection of training variables, healthspan capacities, monitoring, and revision
- [[mental-imagery-for-performance]] — confidence, coping, familiarization, technical rehearsal, sensory fidelity, and evidence limits
- [[skeletal-muscle-hypertrophy]] — mechanosensing, myofibrils, satellite cells, ribosomes, responder variation, aging, and training dose
- [[muscle-damage-and-hypertrophy]] — whether tissue damage is causal, permissive, or a costly by-product of growth-producing tension
- [[cellular-senescence]] — stable arrest, context-dependent SASP, measurement limits, and early senotherapeutic evidence
- [[autophagy-and-lysosomal-quality-control]] — intracellular cargo selection, lysosomal degradation, flux measurement, and intervention limits
- [[mtor-and-rapamycin]] — nutrient sensing, growth–maintenance tradeoffs, mouse longevity, human trials, dosing, and safety
- [[mitochondrial-dysfunction]] — energetics, dynamics, mitophagy, redox signaling, exercise adaptation, and human causal uncertainty
- [[genomic-instability-and-dna-repair]] — DNA lesions, pathway-matched repair, somatic mutation, clonal expansion, and causal boundaries
- [[loss-of-proteostasis]] — folding, chaperones, proteasomal and lysosomal disposal, aggregation, and neurodegeneration
- [[epigenetic-alterations-and-reprogramming]] — chromatin aging, clocks as biomarkers, partial reprogramming, and identity and cancer constraints
- [[stem-cell-exhaustion]] — tissue-specific regenerative decline, niche effects, clonal selection, and intervention limits
- [[telomere-biology]] — chromosome-end protection, replicative limits, short-telomere disorders, population evidence, and cancer tradeoffs
