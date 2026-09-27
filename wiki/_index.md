# Coral Wiki

A living knowledge base built from video transcripts. Organized by entity
type; domains (longevity, nutrition, fitness, hormones, sleep-brain,
skincare, urbanism) live in each page's `tags` frontmatter.

## Sections

- [[_scientific-rigor-audit|Scientific-rigor audit]] — corpus-wide fact-checking status, confirmed corrections, and P0/P1/P2 remediation priorities

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
- Every material claim cites its supporting source nearby. Podcast and video citations establish **provenance only**: they show where an idea entered Coral but do not validate a scientific or clinical claim. Definitions, causal statements, quantitative estimates, outcome claims, safety statements, and recommendations require the strongest applicable scholarly or official evidence.
- **Claim states**: write conclusions so a reader can distinguish established evidence, limited or indirect evidence, expert interpretation, contested claims, and hypotheses. Do not convert a credentialed speaker's confidence into an evidence grade.
- **Clinical evidence order**: current regulator labeling and professional guidance; systematic reviews and meta-analyses; pivotal randomized trials; prospective human studies; mechanistic human research; animal and cell studies; expert interpretation; commercial claims. Study design is not enough by itself—judge population, comparator, endpoint, duration, bias, precision, replication, and applicability.
- **Protocol admission rule**: a dose, schedule, threshold, test cadence, treatment sequence, contraindication, or stopping rule may enter `Practical implications` only when supported nearby by applicable regulatory labeling, professional guidance, an evidence synthesis, or direct human outcome evidence. Otherwise label it `Investigational practice`, preserve its provenance, and state what has not been established.
- **Applicability**: clinical claims identify the population actually studied or covered by guidance, including relevant age, sex, condition, disease stage, baseline risk, and duration. Never extrapolate silently from patients to healthy people, animals to humans, or a selected trial population to everyone.
- **Outcome hierarchy**: distinguish mechanism, biomarker, intermediate outcome, symptoms or function, disease events, quality of life, healthspan, and lifespan. Evidence at one level does not establish benefit at a later level, and a biomarker is not a validated surrogate merely because it predicts risk.
- **Effects and harms**: when available, report absolute effects, comparator risk, uncertainty intervals, study duration, withdrawals, and important adverse outcomes. Relative changes and "percent slowing" must not stand alone when they could exaggerate practical importance.
- **Independence and conflicts**: identify material funding, author, clinic, patent, or commercial interests and whether apparently separate reports reuse the same cohort or dataset. Lack of independent replication lowers confidence.
- **Contradictions and negative evidence**: represent applicable null trials, adverse findings, corrections, retractions, and credible disagreement. Explain population, endpoint, or methodological reasons for conflicting conclusions rather than averaging them into false consensus.
- **Retirement**: archive or consolidate pages whose material content remains predominantly commercial, duplicative, preclinical without a defensible human connection, or unsupported after review. Do not keep a topic actionable merely because it appeared in an episode.
- **Citation integrity has two layers**: automated checks may confirm that a DOI or PMID resolves and carries no detected retraction signal; only a claim-level review can establish that the cited source actually entails the nearby sentence. A page cannot become `current` from link validation alone.
- **Contradiction register**: each reviewed page with credible conflicting evidence keeps an `Evidence conflicts` or `Evidence update` section recording the competing conclusion, source, affected population or endpoint, and current resolution. Material unresolved conflicts remain visible and lower the page's confidence.
- **Evidence decay**: choose `review_interval` by claim volatility and consequence, not one universal cadence. Drug labels, safety warnings, active guidelines, diagnostic tests, and fast-moving trials normally receive 90–180-day review; consequential but comparatively stable clinical evidence 365 days; mature foundational material up to 730 days. Unresolved P0 claims remain `under-review` regardless of interval.
- **Adversarial review**: before a P0 page becomes `current`, perform a second pass that attempts to falsify its conclusion by seeking negative trials, contradictory guidance, important harms, alternate explanations, population mismatches, and dependence among sources. This pass must begin from the claim and evidence, not from the podcast's framing.
- **Diagrams**: when a mechanism, pathway, or system has structure (causal
  chains, feedback loops, decision flows), draw it as a ```mermaid block
  (flowchart or graph) rather than describing it only in prose.
- **Gaps & open questions**: each substantive page keeps a section for
  what is unknown, unmeasured, or understudied — distinct from debates
  (contested claims); a gap is a question nobody has answered yet.
- **Hypothesis development**: the lab develops human-direct hypotheses about low-risk behavior, exercise, nutrition, sleep, adherence, timing, measurement, prevention, and care delivery. Promote an open question only when it has discriminating predictions and can be tested through a feasible human N-of-1, pragmatic, crossover, cohort, or secondary-data design without a wet lab. Cell-, animal-, novel-target-, gene-editing-, and unapproved-compound hypotheses are out of scope. A primary endpoint must measure human function, symptoms, behavior, clinical state, or quality of life—not a biomarker alone. Keep speculation out of the practice playbook. Each hypothesis states its rationale, alternatives, experiment, endpoints, failure criteria, confounders, safety boundary, and status; negative evidence revises or retires it. A Mermaid mechanistic model must show the leveraged node, proposed causal chain, competing pathway, measured endpoints, and important harm branch, with links labeled by evidence strength.
- **Practical implications**: each concept/intervention page states what a
  person should actually do with this knowledge (and at what cadence),
  with the strength of evidence behind it. If no human-facing action survives
  review, say so plainly rather than manufacturing a recommendation.
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
- [[cheese-and-mortality]] — dose-shaped cohort associations, cause-specific mortality, and food-matrix uncertainty
- [[tomato-products-and-lycopene]] — plaque and lipoprotein mechanisms, food-matrix attribution, and outcome limits
- [[nut-consumption-and-mortality]] — total-nut and walnut dose–response associations, diet-quality confounding, and causal limits
- [[performance-nutrition-and-hydration]] — carbohydrate, protein, fluid, electrolytes, GI tolerance, and recomposition
- [[trunk-training]] — flexion, rotation, stabilization functions, loading, and weekly programming
- [[youth-resistance-training]] — physical, cognitive, psychosocial, and lifecourse effects of strength work in children
- [[aging-dynamics-and-resilience]] — longitudinal drift, stress response, recovery, physiological noise, and intervention levels
- [[ai-guided-therapeutic-design]] — target selection, antibody generation, filtering, experimental validation, and translation
- [[stress-threat-discrimination]] — learned appraisal of effort versus danger and prediction-error updating
- [[protective-threat-responses]] — fight, flight, freeze, and the less-settled fawn category
- [[attachment-threat-and-relational-regulation]] — accelerated bonding, withdrawal distress, threat-driven caregiving, and anger that regulates closeness
- [[interpersonal-regulation-and-emotional-capacity]] — shared social load, vigilance cost, depletion, and state-dependent availability
- [[social-evaluative-threat-and-criticism]] — how criticism couples task information to acceptance and status threat
- [[skin-barrier-and-moisturization]] — epidermal water balance, barrier disruption, and function-based moisturization
- [[skincare-evidence-and-routine-design]] — formulation, layering, irritation load, marketing claims, and product value
- [[hair-loss-diagnosis-and-scalp-health]] — diagnosis-first treatment, follicle preservation, cleansing, and evidence tiers
- [[hair-shaft-damage-and-bond-builders]] — keratin structure, chemical damage, water-mediated fragility, cosmetic reinforcement, and evidence limits
- [[topical-retinoids]] — vitamin-A activation, acne and photoaging effects, pigment, and delayed irritation
- [[topical-copper-peptides]] — GHK-Cu mechanisms, vehicle confounding, limited human evidence, combinations, and route-specific safety
- [[topical-peptides]] — peptide classes, delivery limits, the hydration confound, and the topical-versus-injectable risk boundary
- [[photoprotection]] — real-world sunscreen film, reapplication, long-wear claims, and garment care
- [[procedural-skin-remodeling]] — IPL, microneedling, radiofrequency, striae, and botulinum-toxin aftercare
- [[dr-dray]] — dermatologist emphasizing diagnosis, routine simplicity, tolerability, and evidence over prestige
- [[actinic-purpura-and-aging-skin-fragility]] — ultraviolet matrix damage, vessel support, easy bruising, healing, and intervention hierarchy
- [[ebola-virus-disease-and-skin-signs]] — systemic inflammation, endothelial injury, coagulation failure, rash, and recovery signs
- [[erectile-dysfunction-and-vascular-health]] — erectile physiology, vascular sentinel value, apolipoproteins, and cause-directed assessment
- [[testosterone-replacement-therapy]] — diagnosis, physiological replacement, formulation trade-offs, fertility, monitoring, and evidence conflicts
- [[pde5-inhibitors]] — cGMP amplification, established indications, nitrate safety, and systemic evidence boundaries
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
- [[caffeinated-coffee-and-cognitive-aging]] — adenosine antagonism, preclinical amyloid and tau pathways, cohort evidence, sleep trade-offs, and prevention limits
- [[self-schema-updating-after-achievement]] — persistent self-beliefs, corrective evidence, self-talk, and achievement integration
- [[executive-function-under-social-stress]] — shifting, updating, inhibition, post-evaluative load, and the ADHD differential
- [[fiber-gut-skin-axis]] — fiber fermentation, short-chain fatty acids, skin inflammation, and human-evidence limits
- [[cutaneous-signs-of-systemic-disease]] — visible metabolic, hepatic, hematologic, autoimmune, cardiac, and pulmonary clues
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
- [[hallmarks-of-aging]] — enumerative versus coarse-grained frameworks, the 14-hallmark update, and what a framework forbids
- [[extracellular-matrix-aging]] — slow-turnover matrix damage, elastin-fragment immune activation, and environment-imposed cell aging
- [[healthspan-versus-maximum-lifespan]] — whether current rejuvenation therapies are bounded to healthspan, and the stable/unstable species argument
- [[therapeutic-plasma-exchange]] — systemic-milieu replacement, biomarker endpoints, IVIG combination, and treatment burden
- [[spinal-traction-and-fascial-decompression]] — traction versus compression, thoracolumbar fascia, breath-driven decompression, and the "release" terminology dispute
- [[engineered-reprogramming-factors]] — model-designed Yamanaka factors, disordered-sequence design, potency versus rejuvenation, and route-dependent safety
- [[circulating-rejuvenation-signaling]] — parabiosis, dilution and addition designs, aging-by-signaling theory, and what a soluble environment cannot reach
- [[plasma-derived-extracellular-particles]] — preparation, acute tolerability, replication design, endpoints, and the compassionate-use boundary
- [[pig-plasma-fraction-rejuvenation]] — whether a large reported epigenetic rejuvenation in rats is real, and what would settle it
- [[replication-and-research-incentives]] — patents, novelty preference, negative results, and why consequential claims go unchecked
- [[public-trust-in-longevity-science]] — measuring cultural sentiment, demographic clustering, narrative archetypes, and trust as a research input
- [[cultural-legitimacy-versus-research-bottleneck]] — whether public legitimacy or scientific progress is the field's binding constraint
- [[stochastic-aging-and-molecular-noise]] — accumulating regulatory dispersion, quasi-random damage distribution, buffering thresholds, and what noise clocks measure
- [[dream-complex-and-repair-capacity]] — conserved repression of cell-cycle and repair genes, damage resistance on loss of function, and cross-species repair correlates
- [[programmed-versus-stochastic-aging]] — whether developmental-pathway signatures in aging data reflect a running program or a selection effect on repressed genes
- [[engineered-cell-therapy-for-solid-tumors]] — CAR architecture, the targeting, trafficking, and microenvironment failure tree, multiplex base editing, and persistence as a tunable window
- [[open-data-and-research-infrastructure]] — articles as interpretations, dataset annotation levels, effort decay, and reward-side sharing incentives
- [[catastrophizing-and-uncertainty]] — predictive threat completion, false certainty, working-memory load, and action-bounded alternatives
- [[emotional-memory-reactivation-and-rumination]] — distributed autobiographical states, cue retrieval, repetitive rehearsal, and contextual updating
- [[trust-repair-and-safety-learning]] — forgiveness versus trust, competing safety learning, apology, accountability, and behavioral repair
- [[tracey-marks]] — psychiatrist teaching predictive appraisal, memory updating, and behavior-based trust repair
- [[cognitive-dissonance-and-narrative-protection]] — conflict detection, identity-protective reinterpretation, reinforcement, and narrative auditing
- [[lichen-simplex-chronicus]] — itch–scratch reinforcement, barrier injury, neural sensitization, and multimodal interruption
- [[hyperpigmentation-and-dark-spots]] — pigment depth, causal diagnosis, trigger control, and treatment-response boundaries
- [[scars-and-dermal-remodeling]] — hypertrophic collagen, target-matched scar treatment, and site-specific decisions
- [[post-surgical-neuropathic-pain-and-phantom-sensation]] — nerve injury, persistent body maps, phantom symptoms, and assessment
- [[post-weight-loss-skin-laxity]] — tissue-volume mismatch, dermal and adipose support, topical limits, and anatomy-matched treatment
- [[home-skin-photobiomodulation]] — wavelength distributions, irradiance, delivered dose, fit, adherence, and safety
- [[ai-assisted-science-communication]] — probabilistic generation, verification asymmetry, provenance, automation bias, and cognitive offloading
- [[topical-estrogen-for-skin-aging]] — local hormone signaling, uncertain facial absorption, compounding variability, and systemic safety boundaries
- [[systemic-modifiers-of-visible-aging]] — causal and observational evidence for UV, smoking, pollution, menopause, sleep, nutrition, weight change, metabolic disease, and medications
- [[bone-health-osteoporosis-and-fracture-prevention]] — bone strength, DXA and fracture risk, screening, falls, pharmacotherapy, sequencing, and secondary prevention
- [[cyperus-oil-hair-removal]] — unreliable efficacy evidence, unstandardized exposure, and coupled endocrine-safety uncertainty
- [[cosmetic-product-safety-and-regulatory-gaps]] — drug-like lash products, reactive nail systems, prohibited rapid-remover solvents, supply-chain traceability, and packaging controls
- [[genital-restraint-device-safety]] — constriction, pressure, occlusion, consent, release planning, and emergency recognition
- [[coffee-preparation-and-health]] — coffee matrix, filtration, diterpenes, caffeine timing, additives, biomarkers, and outcome limits
- [[exercise-recovery-and-readiness]] — training load, restoration, symptoms, performance, wearables, sleep environment, and modality trade-offs
- [[exercise-intensity-and-health-outcomes]] — outcome-priced intensity, wearable equivalence ratios, exercise snacks, and causal boundaries
- [[sauna-and-deliberate-heat-exposure]] — cardiovascular heat stress, heat-shock proteins, cohort evidence, modality, and temperature limits
- [[deliberate-cold-exposure]] — catecholamine and mitochondrial responses, performance use, and the hypertrophy-timing conflict
- [[sulforaphane]] — NRF2 activation, crucifer preparation, human biomarker evidence, and cancer-outcome limits
- [[vitamin-d]] — synthesis, deficiency, causal inference, repletion, target-level disagreement, and high-dose safety
- [[michelle-wong]] — cosmetic chemist emphasizing claim-level source tracing, formulation context, realistic exposure, and consequence-sensitive safety
- [[pornography-motivation-and-sexual-health]] — arousal, motives, sexual function, media scripts, consent, and causal limits
- [[skincare-pilling-and-film-compatibility]] — layered-film agglomeration, application friction, and sunscreen-coverage implications
- [[phimosis-and-paraphimosis]] — adult foreskin restriction, inflammatory scarring, treatment logic, and emergency paraphimosis
- [[visible-skin-and-facial-aging]] — intrinsic and photoaging across skin, pigment, vessels, fat, retaining structures, muscle, and facial bone
- [[visible-aging-outcomes-and-evidence]] — validated appearance, patient-report, physiological, structural, and photographic endpoints
- [[topical-visible-aging-interventions]] — finished-formula evidence for photoprotection, retinoids, moisturizers, antioxidants, acids, peptides, and growth-factor products
- [[procedures-injectables-and-structural-facial-aging]] — layer-matched lasers, remodeling, neuromodulators, volume replacement, tightening, surgery, durability, and safety
- [[genital-modification-and-sexual-function]] — piercing, enlargement, cosmetic procedures, reversibility, and sexual-function risk
- [[bladder-filling-and-voiding-behavior]] — storage–emptying coordination, learned urgency, delayed voiding, and symptom-aware monitoring
- [[rena-malik]] — urologist using anatomy-first, function-first harm reduction in urinary and sexual health
- [[vulvovaginal-anatomy-and-hormone-sensitivity]] — hormone-responsive vulvar tissues, vestibular pain, examination gaps, and myths about what sex changes
- [[genitourinary-syndrome-of-menopause]] — postmenopausal vulvovaginal and urinary tissue change, local hormone therapy, and the prescribing gap
- [[sexual-desire-arousal-and-aging]] — excitatory–inhibitory desire regulation, responsive desire, and age-shifted stimulation needs and scripts
- [[hormonal-contraception]] — ovulation-suppressing feedback, SHBG and free-testosterone effects, bone accrual, and contraceptive versus menopause dosing
- [[kidney-stones]] — supersaturation chemistry, fluid–sodium–protein–citrate prevention, 24-hour urine testing, and aspiration and office-based lithotripsy
- [[glucosamine]] — brain hyperglycosylation, state-dependent dementia associations, and the MCI/Alzheimer's yellow flag
- [[neuroendocrine-regulation-of-mood]] — estradiol, testosterone, thyroid, and cortisol as system modulators of neurotransmission and mood
- [[mood-disorder-pharmacology]] — episode-based bipolar diagnosis, antidepressant and mood-stabilizer boundaries, adjunctive psychotherapy, ECT, lithium monitoring, and supplement conflicts
- [[ketamine-and-psychedelic-therapy]] — rapid neuroplasticity induction, durable single-dose effects, and unpredictable harm
- [[topical-vitamin-c]] — antioxidant and collagen mechanisms, a thin trial base, formulation constraints, and routine positioning
- [[seborrheic-dermatitis]] — sebum–Malassezia–inflammation mechanism, treatment ladder by causal node, and the unresolved scalp-oil question
- [[vulvovaginal-candidiasis]] — vaginal microflora ecology, real versus mythical risk factors, and recurrence-triggered diagnosis
- [[premature-ejaculation]] — control–bother–latency diagnosis, set-point and anxiety-loop mechanism, partner-perception gap, and expectation-bounded treatment
- [[vitamin-k2]] — matrix Gla protein carboxylation, calcification-slowing trials, and why a lower calcium score is not a validated goal
- [[endurance-exercise-and-coronary-atherosclerosis]] — high-volume training and plaque, masked hypertension, host-health moderation, and the missing outcome data
- [[myostatin-pathway-inhibition]] — precursor and receptor blockade, lean mass versus muscle function, and combination with GLP-1 agonists
- [[lutein]] — carotenoid arterial-imaging benefit against consistently null cardiovascular-outcome evidence
- [[heme-iron-and-colorectal-cancer]] — ferroptosis-resistant iron addiction in established cancer and a mixed occurrence-risk cohort literature
- [[cognitive-behavioral-therapy-for-insomnia]] — sleep restriction, stimulus control, delivery formats, and first-line randomized evidence
- [[obstructive-sleep-apnea]] — upper-airway collapse, intermittent hypoxemia, sleep fragmentation, detection, and treatment verification
- [[insulin-resistance]] — tissue-specific signaling failure, beta-cell compensation, ectopic fat, measurement, and reversal levers
- [[anthocyanins-and-cardiovascular-health]] — flavonoid-class cohort associations, blueberry trial nulls, dose thresholds, and molecule-versus-food attribution
- [[bone-remodeling-and-mechanical-loading]] — osteoclast–osteoblast balance, the load threshold, spaceflight countermeasure evidence, calcium-supplement failure, and the loading ladder
- [[cancer-screening-and-overdiagnosis]] — the screening cascade, overdiagnosis arithmetic, prostate/thyroid/ovarian lessons, whole-body MRI consent, and patient autonomy
- [[blood-pressure-targets-and-frailty]] — SPRINT/ESPRIT intensive targets, frailty-based individualization, home measurement, lowering levers, and secondary causes
- [[sglt2-inhibitors]] — renal glucose excretion, epicardial-fat reduction, mouse-lifespan signal, and indication boundaries
- [[metabolic-liver-disease]] — four-stage MASLD/MASH progression, selective hepatic insulin resistance, visceral-fat and alcohol synergy, and muscle as the competing glucose sink
- [[blood-marker-variability-and-reference-change]] — analytical and biological variation, reference change values, and which serial labs can be tracked at all
- [[dan-garner]] — performance coach using blood-driven constraint finding, adherence-first programming, and measurement-aware protocols
- [[brad-stanfield]] — family physician emphasizing absolute risk, trial applicability, patient autonomy in screening, and lifestyle-first sequencing
- [[azelaic-acid]] — surface-weighted mechanism, prescription versus cosmetic tiers, the pH/free-acid controversy, and derivative limits
- [[cellulite]] — fibrous-septae architecture, fat herniation, subtle retinoid evidence, and the topical ceiling
- [[sweating-and-antiperspirants]] — sweat–bacteria–odor pathway, antiperspirant versus deodorant, irritation culprits, and clinical escalation
- [[nad-metabolism]] — NAD coenzyme roles, synthesis and salvage pathways, PARP consumption, and disease-state versus age-driven decline
- [[nad-precursors-and-healthy-aging]] — whether human anti-inflammatory and PAD trial signals justify routine NR use in healthy people
- [[charles-brenner]] — NR-pathway discoverer with disclosed commercial ties, skeptical of sirtuin, IV-drip, and NAD-decline narratives
- [[meaning-boredom-and-technology]] — coherence, purpose, significance, boredom's cognitive role, and technology's meaning deficit
- [[relationship-maintenance-and-friendship]] — drift repair, real versus deal friends, male friendship decline, and love as the strongest well-being correlate
- [[arthur-brooks]] — happiness scientist teaching the enjoyment–satisfaction–meaning decomposition, wants management, and suffering reframing
- [[rhonda-patrick]] — omega-3 advocacy, nutrient-insufficiency framing, index-targeted dosing, and sponsorship conflicts
- [[primary-headache-disorders]] — migraine, tension-type and cluster patterns, trigeminovascular signaling, red flags, and treatment pathways
- [[health-misinformation-and-media-incentives]] — attention, authority, corrections, affiliate revenue, and claim-level verification
- [[brian-grosberg]] — headache neurologist emphasizing phenotype, diary-guided decisions, and individualized acute/preventive care
- [[gil-carvalho]] — physician-science communicator emphasizing compartments, outcomes, counterevidence, and commercial incentives
- [[hidradenitis-suppurativa]] — follicular skin-fold disease, mechanical and adipose-inflammatory drives, weight loss, diet signals, and GLP-1 adjuncts
- [[psoriasis-and-systemic-inflammation]] — IL-23/IL-17 axis, metabolic–inflammatory coupling, and combination biologic-plus-GLP-1 evidence
- [[diet-and-inflammatory-skin-disease]] — skin sodium storage, IL-17 activation, refined carbohydrate, processed meat, and pattern-level eating
- [[keratosis-pilaris]] — follicular keratin build-up, urea keratolysis, azelaic adjuncts, and transient laser-hair-removal mimics
- [[benign-prostatic-hyperplasia]] — obstructive and storage urinary symptoms, multi-causal frequency, and metabolic-behavioral prevention levers
- [[female-ejaculation-and-squirting]] — mixed bladder and Skene's-gland fluid origin, prevalence versus media expectation, and the orgasm contraction signature
- [[metabolic-drivers-of-pancreatic-cancer]] — hyperinsulinemia-driven acinar injury, glucose-driven proliferation and EMT, and cohort risk associations
- [[tami-rowen]] — sexual-medicine gynecologist teaching arousal non-concordance and group-average versus individual-patient evidence reading
- [[iodine-and-cognitive-development]] — thyroid-hormone substrate, fortification natural experiment, eroding population intake, and the salt-vehicle conflict
- [[personalized-neoantigen-cancer-vaccines]] — central-tolerance escape, per-patient mRNA targeting, melanoma trial trajectory, and generalization limits
- [[meditation-and-contemplative-training]] — trainable well-being pillars, valence-neutral neuroplasticity, five-minute biomarker trials, and brain–immune–gut routes
- [[alpha-hydroxy-acids]] — glycolic and lactic acid exposure logic, in-office versus home depth of action, and 12% ammonium lactate dermal evidence
- [[oats-and-cardiovascular-health]] — beta-glucan viscosity, processing sensitivity, and cohort coronary and all-cause-mortality associations
- [[mastery-learning-and-individualized-tutoring]] — layered prerequisites, fluency and working memory, spaced repetition, motivation design, and unverified AI-school claims
- [[emotions-as-functional-states]] — priority, valence, scalability, persistence, fan-in/fan-out abstraction, fear–panic dissociation, and facial-readout limits
- [[emotion-regulation]] — granularity, strategy timing, amplification risk, flexibility, interpersonal regulation, detachment mechanics, and autonomic training routes
- [[polycystic-ovary-syndrome]] — two-of-three diagnosis, the insulin–androgen loop, and lifelong cardiometabolic risk
- [[sara-gottfried]] — precision-medicine gynecologist emphasizing decade-based biomarker base-casing, anti-progestin positions, and hot flashes as biomarkers
- [[sam-harris]] — meditation teacher separating provisional benefit science from the self-as-illusion claim, two-step-function progress, and psychedelics as proof-of-possibility
- [[memory-encoding-retrieval-and-reconstruction]] — selective encoding, retrieval practice, spacing, reconstructive error, prospective memory, and age-related adaptation
- [[alan-castel]] — memory researcher emphasizing metacognition, corrected retrieval, adaptive selectivity, and successful-aging uncertainty
- [[alice-lichtenstein]] — nutrition scientist emphasizing fat-quality substitutions, dietary patterns, and feasible food-environment change
- [[platelet-rich-plasma-and-fibrin]] — unstandardized autologous preparations, meta-analytic alopecia evidence, rejuvenation limits, and protocol-level consumer questions
- [[paleolithic-diets-and-modern-paleo]] — reconstructed ancestral dietary variety, the expensive-tissue trade-off, and why modern paleo's exclusions fail history and health evidence
- [[nutritional-psychiatry]] — diet-quality–depression evidence, the SMILES trial, microbiome–inflammation–brain mechanisms, fermented foods, and ultra-processed-food boundaries
- [[felice-jacka]] — nutritional-psychiatry founder emphasizing confounder discipline, whole grains, food-matrix limits of balanced UPFs, and structural dietary responsibility
- [[inflammation-and-depression]] — systemic cytokines, the filtered blood–brain barrier, sickness behavior, inflammatory depression subtype, and body-wide sources of low mood
- [[tim-spector]] — genetic epidemiologist and ZOE co-founder: microbiome diversity, UPF policy advocacy, brain-disorder unification, and disclosed commercial conflicts
- [[federica-amati]] — clinical nutritionist teaching the four-stage appetite cascade and phased nutritional support around GLP-1 therapy
- [[ultra-processed-food]] — monoculture-to-formulation supply chain, engineered hyperpalatability, the food-addiction question, and identification heuristics
- [[culinary-mushrooms-and-fungal-nutrition]] — fungal-kingdom chemistry, UV-dependent vitamin D, ergothioneine, beta-glucans, the mycobiome, and preparation
- [[gut-virome-and-bacteriophages]] — commensal phage ecology, lytic and lysogenic control of gut bacteria, mucus-layer defense, and diversity–health correlations
- [[phage-therapy]] — antimicrobial resistance, matched-phage treatment history and case evidence, microbiome sparing, and engineered delivery
- [[michael-pollan]] — food journalist behind the eat-food-mostly-plants frame, monoculture critique, cooking advocacy, and the food-addiction position shift
- [[adhd-dysregulation-and-rejection-sensitivity]] — multi-domain dysregulation, rejection-sensitive dysphoria, novelty-driven attention, stimulant mechanism, and ADHD sleep
- [[microglia-and-neuroinflammation]] — brain-immune activation states, the immunometabolic convergence thesis, mitochondrial toxins, TSPO imaging, and reversibility claims
- [[david-perlmutter]] — preventive neurologist behind the metabolic-brain framing, early contrarian calls, position reversals, and contested gluten claims
- [[lucy-mcbride]] — primary-care internist teaching the question beneath the question, biographic-plus-biometric health data, and inward locus of control
- [[skin-cancer-risk-and-immune-surveillance]] — UV dose plus immune surveillance as joint causes, rising young-adult incidence, early-detection signs, and the contested old-sunburn question
- [[chronic-itch-and-pruritus]] — itch as neural disease, age-structured etiology, barrier-first treatment, and phototherapy for refractory cases
- [[uv-phototherapy]] — controlled narrowband UVB dosing for psoriasis, eczema, vitiligo, itch, and CTCL
- [[boundaries-and-overcommitment]] — the yes/no asymmetry, commitment load and burnout, refusal as trainable skill, and concentrated effort with designed rest
- [[teo-soleymani]] — skin cancer surgeon arguing safe sun exposure over avoidance, immune-centric cancer framing, and a minimalist sunscreen-retinoid-lifestyle routine
- [[david-rabin]] — psychiatrist teaching felt safety as the gate on learning, anxiety as signal, bottom-up safety cues, and conflicted psychedelic-therapy advocacy
- [[exfoliation-and-desquamation]] — natural shedding, chemical and mechanical routes, hidden cumulative exfoliation load, over-exfoliation signs, and moisturization as the upstream lever
- [[maria-sophocles]] — gynecologist teaching the bedroom gap, graded desire re-engagement, erotic memory, and communication-as-lubrication
- [[indoor-air-quality]] — sealed-envelope accumulation, source control before filtration, CO2 and cognition, and the thin intervention-trial base
- [[body-image-and-appearance-change]] — appearance change versus reframing, dysmorphia's objectivity test, comparison toxicity, and the leanness cost curve
- [[mike-israetel]] — exercise scientist pricing physique goals in explicit trade-offs, defending vanity as motive, and objective progression over feel
- [[will-cole]] — functional-medicine clinician behind the cellular-confusion frame, organ-aging popularization, and flagged EMF-mold and C15 speculation
- [[nutrient-density-and-food-profiling]] — profiling-algorithm design choices, the sodium-to-potassium processing proxy, the processed-meat gradient, and policy surfaces
- [[ty-beal]] — nutrition researcher behind the Nutritional Value Score, the Food Compass critique, and the processed-meat continuum
- [[essential-amino-acid-supplementation]] — leucine signaling, anabolic resistance, stress-based-physiology use cases, and commercial-claim hazards
- [[partner-search-and-dating-behavior]] — search costs, the realism–romanticism balance, intimacy-triggered withdrawal, and discourse-sample distortion
- [[continuous-glucose-monitoring]] — interstitial sensing, population-specific benefit, normal excursions, structured biofeedback, and missing durable outcomes
- [[dietary-protein-and-cardiovascular-risk]] — protein quantity versus source, substitution, ApoB, muscle, anabolic-steroid confounding, and the older-adult evidence conflict
