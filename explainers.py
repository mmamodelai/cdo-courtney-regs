"""Plain-English explainers for every regulation in the Tier-1 catalog.

AUTHORED editorial content (curation, like the topic registry) — NOT scraped.
Written so a reviewer (Eddie/Melissa) or a customer can understand what each
regulation actually requires WITHOUT opening the legal text: what it is, who it
applies to, and the concrete obligations/numbers that matter on a roofing job.

build_dashboard.py joins these to the live DB rows by citation and WARNS about
any regulation that lacks an explainer, so coverage stays complete as the
catalog grows.
"""

EXPLAINERS = {
    # ================= CA — Cal/OSHA Title 8 (safety) =================
    "8 CCR § 1669":
        "The general California fall-protection rule for construction: workers exposed to falls "
        "must be protected by an approved system (guardrails, personal fall arrest/restraint, or "
        "positioning devices). It's the umbrella section that the more specific roofing rules "
        "(§1724/1730/1731) hang from. If a crew member can fall and no system is in place, this "
        "is the section Cal/OSHA cites.",
    "8 CCR § 1670":
        "The nuts-and-bolts requirements for personal fall arrest, fall restraint, and positioning "
        "systems in California construction: full-body harness required, anchorage strength minimums "
        "(5,000 lbs or engineered 2:1 safety factor), max free-fall distance, inspection before each "
        "use, and removal from service after a fall. This is the standard your harness/lanyard/anchor "
        "program must satisfy on every roof.",
    "8 CCR § 1671":
        "Safety-net requirements when nets are the chosen fall protection: where nets may be used, "
        "how far below the work surface they may hang, mesh/border strength, and drop-testing. Mostly "
        "relevant on larger commercial jobs — but if a net is on site, this is its rulebook.",
    "8 CCR § 1724":
        "The general roofing-operations article for California: requirements that apply to ALL roofing "
        "work — surface inspection before work starts, material handling and staging on roofs, and "
        "weather/access precautions. It is the entry point for Cal/OSHA's roofing-specific rules.",
    "8 CCR § 1730":
        "California's 'roof hazards' standard for non-residential roofing: defines when fall protection "
        "is required by roof slope and height, warning lines, hoisting areas, and roof-edge rules. "
        "Together with §1731 it is the controlling CA authority for roof tear-off fall protection — "
        "stricter than the federal floor.",
    "8 CCR § 1731":
        "Residential-type roofing in California, explicitly including roof REMOVAL/tear-off. Key "
        "numbers (amended eff. July 1, 2025): slopes steeper than 7:12 need fall protection at ANY "
        "height; 0:12–7:12 slopes need it at 6 ft. This is the single most directly applicable fall "
        "rule for a residential tear-off crew.",
    "8 CCR § 3395":
        "California's outdoor Heat Illness Prevention standard — there is NO federal equivalent yet. "
        "Requires: fresh water (1 qt/hr per worker), shade at 80°F+, a written Heat Illness Prevention "
        "Plan, training, and HIGH-HEAT procedures at 95°F+ (mandatory rest/water breaks, observation, "
        "communication). Roofing is one of the highest-risk trades; Cal/OSHA actively enforces this "
        "every summer.",
    "8 CCR § 1529":
        "California's construction asbestos standard. Old roofs (mastics, felts, transite, pre-1981 "
        "materials) routinely contain asbestos — this section sets exposure limits (PEL 0.1 f/cc), "
        "work classifications (Class I–IV), required wet methods, respirators, medical surveillance, "
        "and the requirement to presume asbestos in pre-1981 materials until tested. Disturbing old "
        "roofing without an asbestos determination is a serious-citation risk.",
    "8 CCR § 1532.1":
        "California's construction lead standard. Lead shows up in old flashing, solder, and paints "
        "disturbed during tear-off. Sets a PEL of 50 µg/m³ (8-hr TWA), trigger tasks that require "
        "interim protection (respirators, change areas, blood-lead monitoring) until exposure is "
        "assessed, plus hygiene and training requirements. CDPH work-practice rules ride on top of it.",
    "8 CCR § 1532.3":
        "California's respirable crystalline silica standard for construction. Cutting/grinding tile, "
        "concrete, or fiber-cement triggers it. PEL 50 µg/m³, Action Level 25 µg/m³. Employers either "
        "follow Table 1's specified controls per task (wet saws, vacuum shrouds, respirators) or do "
        "their own air monitoring. Above the PEL 30+ days/year → medical surveillance. A written "
        "Exposure Control Plan is mandatory.",
    "8 CCR § 5144":
        "California's respiratory-protection program standard (mirrors federal 1910.134). If ANY task "
        "requires a respirator — asbestos, silica, lead dust — this section requires a written program, "
        "medical evaluation BEFORE first use, annual fit testing, training, and cleaning/storage rules. "
        "Handing a worker an N95 or half-face respirator without the program is itself a violation.",
    "8 CCR § 1514":
        "The construction-orders PPE hook: requires employers to provide and require the use of personal "
        "protective equipment per the General Industry Safety Orders (Article 10, §3380+). The detailed "
        "head/eye/hand/foot requirements live in the §3380-series — the old construction-specific PPE "
        "sections (§1515–1520) were repealed.",
    "8 CCR § 3380":
        "California's umbrella PPE rule (GISO Article 10): employers must assess hazards, select and "
        "provide appropriate PPE at no cost to the worker, ensure it fits, and train on its use. The "
        "specific body-part standards (§3381–3385) hang off this section. This is the Critical-30 "
        "PPE citation.",
    "8 CCR § 3381":
        "Hard-hat requirement: head protection (ANSI Z89.1) must be worn where there's risk of impact, "
        "falling/flying objects, or electrical shock — which describes essentially every active tear-off "
        "site with debris coming off a roof. Employer provides; employer enforces.",
    "8 CCR § 3382":
        "Eye and face protection (ANSI Z87.1): required for flying particles, dust, and chemical "
        "exposure — nailing, cutting, grinding, demo work. Includes side-protection and prescription-"
        "lens accommodation requirements. This GISO section replaced the repealed construction §1516.",
    "8 CCR § 3383":
        "Body protection: appropriate clothing/protective garments for the hazard — e.g., protection "
        "against hot asphalt/tar in built-up roofing, abrasion, and sun exposure. Selection follows "
        "the §3380 hazard assessment.",
    "8 CCR § 3384":
        "Hand protection: gloves matched to the hazard — cut resistance for sheet metal/demo, heat "
        "resistance for hot work, chemical resistance for adhesives/solvents. Replaced the repealed "
        "construction §1520.",
    "8 CCR § 3385":
        "Foot protection (ASTM F2413): protective footwear where falling/rolling objects, punctures "
        "(nails — ubiquitous on tear-off), or hot surfaces are present. Replaced the repealed "
        "construction §1517.",
    "8 CCR § 3203":
        "THE foundational California safety requirement: every employer must have a written, "
        "site-implemented Injury & Illness Prevention Program (IIPP) — responsible person named, "
        "hazard inspections on a schedule, accident investigation, hazard correction, training at "
        "hire/new task/new hazard, and a way for workers to report hazards without fear. It's "
        "Cal/OSHA's most-cited standard; an inspector asks for the IIPP first, on every visit.",
    "8 CCR § 5194":
        "California's Hazard Communication standard (controlling over federal HazCom in CA, and adds "
        "Prop 65). Requires: a written HazCom program, a chemical inventory, Safety Data Sheets "
        "accessible to workers, GHS labeling, and training on every hazardous chemical on site — "
        "adhesives, primers, solvents, hot asphalt. Construction-specific provisions at (f)(7).",
    "8 CCR § 3314":
        "Lockout/Tagout — controlling hazardous energy when cleaning, servicing, or adjusting machinery "
        "and equipment. For roofing: conveyors, hoists, kettles, and powered equipment must be de-"
        "energized and locked/tagged before service. Requires written procedures, training, and "
        "periodic inspection of the program.",
    "8 CCR § 3221":
        "Written Fire Prevention Plan: identify ignition sources and fuel hazards (torch-applied "
        "roofing, kettles, fuel storage), housekeeping to control them, maintenance of heat-producing "
        "equipment, and employee training on fire hazards of their work. Pairs with hot-work practices "
        "on torch-down jobs.",
    "8 CCR § 3400":
        "Medical services & first aid: a person trained in first aid must be AVAILABLE on every "
        "jobsite, suitable first-aid kits on site, and (where no infirmary/clinic is near) written "
        "emergency procedures. For dispersed roofing crews this effectively means first-aid/CPR "
        "training for foremen — which is exactly how the Critical-30 maps it.",
    "8 CCR § 1950":
        "Confined Spaces in Construction (Article 37, §§1950–1962, updated eff. Jan 1, 2026): scope "
        "section for the construction-specific confined-space rules — identification of spaces, entry "
        "permits, atmospheric testing, attendants, and rescue. For roofing this hits attics, plenums, "
        "tanks, and mechanical penthouses. Do NOT cite general-industry §5157 for construction work.",

    # ================= Federal — OSHA 29 CFR 1926 (construction) =================
    "29 CFR § 1926.500":
        "Scope and definitions for federal Subpart M (fall protection): defines the terms every other "
        "fall rule uses — unprotected side/edge, low-slope vs steep roof, leading edge, anchorage, "
        "competent person. Included so the defined terms behind §§501–503 are part of the record.",
    "29 CFR § 1926.501":
        "The federal duty to provide fall protection: 6 ft above a lower level in construction. For "
        "roofing specifically — low-slope roofs may use guardrails, nets, PFAS, or a warning-line + "
        "safety-monitor combo ((b)(10)); steep roofs require guardrails with toeboards, nets, or PFAS. "
        "This is the federal floor; CA's §1730/1731 are stricter and control in California.",
    "29 CFR § 1926.502":
        "The engineering criteria behind every federal fall-protection system: guardrail heights and "
        "strength (42\" ±3\", 200 lbs), personal fall arrest specs (5,000-lb anchors, max arresting "
        "forces, free-fall limits), warning-line and safety-monitor rules, and covers for roof "
        "openings. If §501 says 'protect', §502 says exactly what compliant protection looks like.",
    "29 CFR § 1926.503":
        "Federal fall-protection TRAINING requirements: every worker exposed to fall hazards must be "
        "trained by a competent person to recognize fall hazards and use the systems on site; the "
        "employer must keep a WRITTEN certification (name, date, trainer signature) and retrain when "
        "conditions, equipment, or worker performance show the training didn't stick. This is the "
        "citation behind CDO's fall-protection training requirement.",
    "29 CFR § 1926.95":
        "The federal umbrella PPE rule for construction: protective equipment for eyes, face, head, and "
        "extremities must be provided, used, and maintained wherever hazards are present — and the "
        "employer pays for required PPE. The body-part specifics live in §§96–102.",
    "29 CFR § 1926.96":
        "Federal foot-protection rule: safety-toe footwear meeting the ANSI standard where foot injury "
        "hazards exist. Short section — the substance is the referenced ANSI/ASTM spec.",
    "29 CFR § 1926.100":
        "Federal hard-hat rule: helmets required where there is possible danger of head injury from "
        "impact, falling/flying objects, or electrical shock/burns. Must meet ANSI Z89.1.",
    "29 CFR § 1926.101":
        "Federal hearing protection: where noise can't be reduced below the Table D-2 levels in "
        "§1926.52, ear protective devices must be provided and used; plain cotton is explicitly not "
        "acceptable. Relevant around saws, compressors, and tear-off equipment.",
    "29 CFR § 1926.102":
        "Federal eye/face protection: ANSI Z87.1 protection required for flying objects, glare, "
        "liquids, and radiant energy — with a selection table by operation (chipping, cutting, "
        "welding shades) and prescription-eyewear rules.",
    "29 CFR § 1926.103":
        "A one-line cross-reference: federal construction respiratory protection IS general-industry "
        "§1910.134. We hold the full 1910.134 text as its own row — review that one for the substance; "
        "this row exists so the construction-side citation resolves.",
    "29 CFR § 1926.55":
        "Federal exposure limits for gases, vapors, fumes, dusts, and mists in construction: keep "
        "exposures under the Appendix A threshold limit values, prefer engineering/administrative "
        "controls, use respirators per §134 when controls aren't feasible. This is the catch-all "
        "air-contaminant rule behind fumes from kettles, adhesives, and dust.",
    "29 CFR § 1926.62":
        "Federal construction lead standard: PEL 50 µg/m³ (8-hr TWA), action level 30 µg/m³. Specific "
        "'trigger tasks' (demolition of lead-painted surfaces, torch work) require interim protection "
        "— supplied-air or HEPA respirators, protective clothing, blood-lead testing — until the "
        "employer proves exposure is below limits. Old flashing and paints make this real on tear-offs.",
    "29 CFR § 1926.1101":
        "Federal construction asbestos standard — the longest rule in our catalog (233K chars) because "
        "it's effectively a complete program: work classes I–IV, PEL 0.1 f/cc, presumed asbestos in "
        "pre-1981 buildings, competent persons, regulated areas, wet methods, decontamination, medical "
        "surveillance, and disposal. Roofing felts/mastics are explicitly addressed (Class II work).",
    "29 CFR § 1926.1153":
        "Federal respirable crystalline silica in construction: PEL 50 µg/m³, action level 25 µg/m³. "
        "Table 1 lists 18 task categories (masonry saws, grinders, drills) with specified controls — "
        "follow Table 1 exactly and you're deemed compliant; otherwise monitor air. Requires a written "
        "exposure control plan and a designated competent person. Tile and fiber-cement work is where "
        "roofers hit this.",
    "29 CFR § 1926.59":
        "A one-line cross-reference: federal construction HazCom IS general-industry §1910.1200. We "
        "hold the full 1910.1200 text as its own row — review that one for the substance. In California "
        "the controlling standard is 8 CCR §5194.",
    "29 CFR § 1926.250":
        "Federal material-storage rules: stored materials must not create hazards — secured against "
        "sliding/collapse, aisles kept clear, and (critically for roofing) materials stored on roofs "
        "must be stacked/secured so they can't slide or blow off, with weight limits respected.",
    "29 CFR § 1926.252":
        "Federal waste-disposal rule for demolition/tear-off: debris dropped more than 20 ft must go "
        "through an enclosed chute; drop areas must be barricaded and signed; debris can't accumulate "
        "into a hazard. This is THE federal citation for how tear-off debris legally leaves a roof.",
    "29 CFR § 1926.451":
        "Federal scaffold general requirements: capacity (4:1 safety factor), platform construction, "
        "max gaps, safe access (no climbing cross-braces), fall protection at 10 ft on scaffolds, and "
        "competent-person inspection before each shift. Applies whenever staging or supported "
        "scaffolds are used for roof access or edge work.",
    "29 CFR § 1926.1051":
        "Federal stairway/ladder access rule: a stairway or ladder is REQUIRED at any access point "
        "with a 19-inch or greater elevation break — i.e., getting on a roof requires a compliant "
        "ladder, and workers must be trained on ladder hazards (§1060).",
    "29 CFR § 1926.1053":
        "Federal ladder specifications and use: side rails extending 3 ft above the landing, secured "
        "against displacement, 4:1 setup angle, no carrying loads that cause loss of balance, "
        "defective ladders tagged out. Ladder misuse is among the most-cited violations in roofing.",
    "29 CFR § 1910.1200":
        "The FULL federal Hazard Communication standard (construction §1926.59 just points here): "
        "written program, chemical inventory, GHS-compliant labels, Safety Data Sheets accessible on "
        "site, and effective worker training — in a language workers understand — on every hazardous "
        "chemical. This row carries the complete 300K-char text so the actual obligations are in our "
        "database, not just a pointer.",
    "29 CFR § 1910.134":
        "The FULL federal Respiratory Protection standard (construction §1926.103 just points here): "
        "written respirator program with a designated administrator, medical evaluation BEFORE first "
        "use, annual fit testing, seal checks, maintenance/storage rules, and specific procedures for "
        "voluntary N95 use (Appendix D). Any asbestos/silica/lead task that puts a respirator on a "
        "face makes this entire program mandatory.",

    # ================= Federal — employment law =================
    "29 CFR § 825.100":
        "FMLA overview: covered employers (50+ employees) must give eligible workers up to 12 weeks "
        "of job-protected, unpaid leave per year for serious health conditions, new children, or "
        "qualifying military family needs — with group health benefits maintained and reinstatement "
        "to the same/equivalent job. Federal floor; CA's CFRA applies at just 5 employees.",
    "29 CFR § 825.112":
        "The qualifying reasons for FMLA leave, spelled out: birth/bonding, adoption/foster placement, "
        "the employee's own serious health condition, caring for a spouse/child/parent with one, and "
        "military exigencies/caregiving. Useful as the checklist for whether a leave request is "
        "FMLA-protected.",
    "29 CFR § 825.200":
        "The FMLA amounts: 12 workweeks in a 12-month period (employer may choose the 12-month "
        "measuring method, e.g. rolling), and up to 26 weeks for military caregiver leave. Defines "
        "how intermittent leave counts against the entitlement.",
    "29 CFR § 778.107":
        "The federal overtime baseline (FLSA): non-exempt employees get 1.5× their regular rate after "
        "40 hours in a workweek. California adds daily overtime on top (LAB §510) — in CA you comply "
        "with BOTH, applying whichever rule pays more for a given hour.",
    "29 CFR § 541.100":
        "The FLSA executive exemption test — what it takes for a manager to be legally exempt from "
        "overtime: salary basis at the federal minimum threshold, primary duty of management, directing "
        "2+ employees, and hire/fire authority or weight. Misclassifying foremen as exempt is a "
        "classic construction wage violation; CA's exemption test is stricter still.",
    "29 CFR § 1630.2":
        "ADA definitions (15+ employees): what counts as a disability, what 'reasonable accommodation' "
        "and 'undue hardship' mean, and 'direct threat'. These definitions drive every accommodation "
        "conversation — including return-to-work after injuries, which roofing sees often.",
    "29 CFR § 1630.9":
        "The ADA's operative duty: employers must provide reasonable accommodation to qualified "
        "individuals with disabilities unless it causes undue hardship — and may not deny jobs to "
        "avoid accommodating. The interactive process with the employee is the practical requirement "
        "here. CA's FEHA mirrors this at 5+ employees.",
    "29 CFR § 1604.11":
        "The EEOC's sexual-harassment guidelines under Title VII: defines quid pro quo and hostile-"
        "environment harassment, employer liability for supervisors/coworkers/non-employees, and the "
        "duty to prevent and promptly correct. CA layering: FEHA + mandatory SB 1343 training.",
    "20 CFR § 1002.5":
        "USERRA definitions: who is protected (uniformed service members, reservists, National Guard), "
        "what counts as 'service in the uniformed services', and key terms (seniority, escalator "
        "position) used by the reemployment rules. Applies to ALL employers regardless of size.",
    "20 CFR § 1002.18":
        "USERRA's anti-discrimination core: employers may not deny hiring, reemployment, promotion, or "
        "any benefit because of military service or obligations — and may not retaliate. There is no "
        "small-employer exception.",
    "20 CFR § 1002.180":
        "USERRA reemployment right: a returning service member is entitled to prompt reemployment in "
        "the position they would have attained had they never left (the 'escalator' principle), with "
        "seniority and benefits, if they gave notice, served under 5 cumulative years, and returned/"
        "applied within the deadlines. Pairs with CA Mil. & Vet. Code §394.",

    # ================= CA — statutes (Labor / Gov / B&P / Civ / Veh / MVC) =================
    "Cal. Lab. Code § 510":
        "California daily overtime — stricter than federal: 1.5× after 8 hours in a DAY or 40 in a "
        "week and for the first 8 hours on the 7th consecutive day; 2× after 12 hours in a day or "
        "after 8 on the 7th day. Note: crews under a valid collective bargaining agreement or Wage "
        "Order 16 alternative workweek may have different schedules.",
    "Cal. Lab. Code § 512":
        "Meal periods: a 30-minute unpaid, duty-free meal before the END of the 5th hour of work, and "
        "a second before the end of the 10th. Miss one and the employer owes a premium hour of pay. "
        "For construction crews, Wage Order 16 adds the on-site specifics and CBA exceptions.",
    "Cal. Lab. Code § 226":
        "Itemized wage statements: every pay stub must show 9 things — gross wages, total hours, "
        "piece rates if any, all deductions, net wages, pay-period dates, employee name + last 4 of "
        "SSN, employer's full name/address, and all hourly rates with hours at each. Violations carry "
        "per-employee penalties and are a favorite of PAGA lawsuits.",
    "Cal. Lab. Code § 201":
        "Final pay on termination: ALL earned wages — including accrued, unused vacation — are due "
        "IMMEDIATELY at the moment of discharge. Not end of week, not next payroll. Immediately.",
    "Cal. Lab. Code § 202":
        "Final pay on resignation: due within 72 hours of quitting — or immediately if the employee "
        "gave at least 72 hours' notice.",
    "Cal. Lab. Code § 203":
        "The teeth behind §§201/202: willfully late final pay accrues a 'waiting-time penalty' of one "
        "full day of wages per day late, up to 30 days. A $240/day worker paid 30 days late costs "
        "$7,200 in penalty alone.",
    "Cal. Lab. Code § 1182.12":
        "The state minimum wage statute with its scheduled increases and the annual CPI adjustment "
        "mechanism. Reality check: many cities/counties set HIGHER local minimums, and prevailing-wage "
        "jobs pay far above this — but this is the legal floor every CA paycheck must clear.",
    "Cal. Lab. Code § 2810.5":
        "Wage Theft Prevention Act notice: at hire, every non-exempt employee must receive a WRITTEN "
        "notice stating pay rate(s), overtime rates, pay day, employer's legal name/addresses, "
        "workers' comp carrier, and paid-sick-leave rights — plus written notice within 7 days of any "
        "change. The DLSE publishes a template form.",
    "Cal. Lab. Code § 246":
        "California paid sick leave (HWHFA): accrual of at least 1 hour per 30 worked (or front-load "
        "40 hours/5 days), use after 90 days, carryover with caps, no payout at separation required, "
        "and pay-stub disclosure of the balance. Applies to virtually every employee including "
        "part-time and seasonal crews.",
    "Cal. Lab. Code § 233":
        "'Kin care': employees may use up to half their annual sick-leave accrual to care for a sick "
        "family member (broadly defined). An employer can't discipline someone for using sick leave "
        "this way.",
    "Cal. Gov. Code § 12945.2":
        "CFRA — California's family/medical leave, applying at just 5 EMPLOYEES (vs FMLA's 50): up to "
        "12 weeks of job-protected leave for the employee's or a family member's serious health "
        "condition or for bonding, with a broader family-member definition than FMLA (includes "
        "siblings, grandparents, parents-in-law, designated persons).",
    "Cal. Gov. Code § 12945":
        "Pregnancy Disability Leave: up to 4 MONTHS of job-protected leave per pregnancy for "
        "disability from pregnancy/childbirth, at 5+ employees — separate from, and in ADDITION to, "
        "CFRA bonding leave. Also requires reasonable accommodation (e.g., modified duties) for "
        "pregnant employees.",
    "Cal. Gov. Code § 12945.7":
        "Bereavement leave (AB 1949): at 5+ employees, up to 5 days of protected bereavement leave "
        "per death of a qualifying family member, taken within 3 months; may be unpaid but employees "
        "can use accrued paid time.",
    "Cal. Lab. Code § 230":
        "Protected civic/victim time off: jury duty, court appearances as a crime victim, and time "
        "off + reasonable accommodations for victims of domestic violence, sexual assault, or "
        "stalking. No firing or discrimination for taking it; some pieces apply at 25+ employees.",
    "Cal. Lab. Code § 230.8":
        "School-activities leave at 25+ employees: up to 40 hours/year (max 8/month) of protected "
        "time off for a parent/guardian to participate in a child's school or daycare activities, "
        "using existing vacation/PTO.",
    "Cal. Gov. Code § 12940":
        "FEHA — California's main anti-discrimination/harassment statute, stronger than federal law: "
        "protected classes include race, religion, sex/gender identity, sexual orientation, age 40+, "
        "disability, and more; applies at 5+ employees (harassment: ANY size); imposes a standalone "
        "duty to take reasonable steps to PREVENT harassment; personal liability possible for "
        "harassers. This is the statute behind most CA employment lawsuits.",
    "Cal. Gov. Code § 12950.1":
        "Mandatory sexual-harassment-prevention training (SB 1343) at 5+ employees: 2 hours for "
        "supervisors, 1 hour for all other employees, within 6 months of hire/promotion and every 2 "
        "years after. Seasonal/temporary workers must be trained within 30 days or 100 hours. Records "
        "must be kept — this maps directly to a CDO training requirement.",
    "Cal. Lab. Code § 6401.9":
        "Workplace Violence Prevention Plan (SB 553, eff. July 2024): nearly every CA employer must "
        "have a written WVPP — violence hazard assessment, incident log, response procedures, and "
        "annual training. New enough that many contractors don't have one; an easy first compliance "
        "win for CDO to flag.",
    "Cal. Lab. Code § 3700":
        "Workers' compensation insurance is MANDATORY for every CA employer with even one employee. "
        "Operating uninsured is a criminal offense and triggers stop-work orders + penalties; for "
        "contractors it also voids the CSLB license. The compliance engine should treat a lapsed comp "
        "policy as a hard red flag.",
    "Cal. Bus. & Prof. Code § 7065":
        "CSLB licensing — the examination/experience requirements to hold a contractor's license. For "
        "a roofing company the operative license is the C-39 classification; an expired or suspended "
        "license makes every contract potentially unenforceable and all work unlicensed contracting.",
    "Cal. Lab. Code § 1771":
        "Prevailing wage: on public works projects over $1,000, workers must be paid the DIR-"
        "determined prevailing rate for their craft and county — typically far above market wage. "
        "This is the trigger statute; rates come from DIR determinations updated twice a year.",
    "Cal. Lab. Code § 1775":
        "Prevailing-wage penalties: up to $200 PER WORKER PER DAY of underpayment, plus back wages — "
        "and the prime contractor is liable for subs' violations. Certified payroll (eCPR) is how DIR "
        "checks. This is why the engine needs a jobs.is_public_works flag.",
    "Cal. Lab. Code § 1777.5":
        "Apprenticeship on public works: contracts ≥ $30K require employing registered apprentices at "
        "a 1:5 apprentice-to-journeyman hours ratio, contributing to the apprenticeship fund, and "
        "requesting dispatch from local programs. Frequently missed by contractors new to public work.",
    "Cal. Lab. Code § 2802":
        "Expense reimbursement: employers must reimburse ALL necessary business expenses — personal "
        "phone used for work, mileage between sites, required tools above the Wage Order allowance. "
        "Unreimbursed-expense class actions are common; a clear reimbursement policy is the defense.",
    "Cal. Lab. Code § 551":
        "One sentence of law: every worker is entitled to one day's rest in seven. The operative "
        "prohibition is §552 (next row). Per Mendoza v. Nordstrom, measured by the workweek, and "
        "employees may voluntarily choose to work 7 — but the employer can't cause it.",
    "Cal. Lab. Code § 552":
        "The day-of-rest prohibition with teeth: no employer may CAUSE employees to work more than 6 "
        "days in 7 (workweek basis). Exceptions exist for emergencies and for weeks where total hours "
        "don't exceed 30 (no day over 6). Schedule-building in CDO should warn on 7-day patterns.",
    "Cal. Lab. Code § 432.3":
        "Pay transparency: employers may not ask applicants for salary history; must provide a pay "
        "scale on request; and at 15+ employees must INCLUDE the pay scale in every job posting. "
        "Civil penalties per violation.",
    "Cal. Lab. Code § 1198.5":
        "Personnel-file access: current and former employees may inspect/copy their personnel records; "
        "employer must comply within 30 days (max 50 requests/yr from former employees). Pairs with "
        "§226(b) pay-record access. CDO's document vault makes this trivially satisfiable.",
    "Cal. Lab. Code § 1030":
        "Lactation break time: reasonable break time to express milk, running concurrently with paid "
        "breaks where possible (unpaid beyond them). One of three lactation sections — §1031 covers "
        "the space, §1034 the room specs.",
    "Cal. Lab. Code § 1031":
        "Lactation space: a private location close to the work area that is NOT a bathroom. For field "
        "crews this is a real logistics question (job-site trailer, vehicle policy) worth a written "
        "procedure.",
    "Cal. Lab. Code § 1034":
        "Lactation room requirements (SB 142): the space must be safe, clean, free of toxic materials, "
        "have a surface and seating, and access to electricity plus a sink and refrigeration close by. "
        "Denying adequate space is treated as a failure to provide a rest period (premium pay).",
    "Cal. Mil. & Vet. Code § 394":
        "California's military-leave protection: no discrimination or discharge because of National "
        "Guard/reserve membership or service, with reinstatement rights. The federal counterpart "
        "(USERRA, 20 CFR 1002) applies in parallel — comply with both.",
    "Cal. Gov. Code § 12952":
        "Fair Chance Act (ban-the-box) at 5+ employees: no criminal-history questions until AFTER a "
        "conditional job offer; then an individualized assessment, written preliminary notice, 5 "
        "business days to respond, and a final written decision. A standardized hiring flow in CDO "
        "keeps this clean.",
    "Cal. Lab. Code § 1102.5":
        "Whistleblower protection: employees can't be retaliated against for reporting suspected legal "
        "violations internally OR to any government agency — including Cal/OSHA complaints about "
        "safety. Penalties up to $10K per violation plus a 2024-strengthened presumption of "
        "retaliation for adverse action within 90 days of protected activity.",
    "Cal. Lab. Code § 2775":
        "AB 5's ABC test, codified: a worker is an EMPLOYEE unless the hirer proves all three — (A) "
        "free from control, (B) work outside the hiring entity's usual business, and (C) an "
        "independently established trade. Prong B makes a 1099 'roofer' working for a roofing company "
        "nearly impossible; subcontractors must hold their own CSLB license (B&P §2750.5 overlay) to "
        "be legitimate.",
    "Cal. Gov. Code § 100032":
        "CalSavers: every CA employer with ≥1 eligible employee must either offer a qualified "
        "retirement plan or register for the state CalSavers program and facilitate payroll "
        "deductions. Penalties of $250–$500 per eligible employee for ignoring it.",
    "Cal. Lab. Code § 980":
        "Social-media privacy: employers can't demand usernames/passwords for personal accounts or "
        "require an employee to access them in the employer's presence. Keep it out of hiring and "
        "investigations.",
    "Cal. Civ. Code § 3426.1":
        "Uniform Trade Secrets Act definitions: what qualifies as a trade secret (economic value from "
        "secrecy + reasonable efforts to keep secret) and what 'misappropriation' means. The legal "
        "basis for confidentiality provisions protecting customer lists and bid pricing.",
    "Cal. Veh. Code § 23123.5":
        "Hands-free driving: no holding a phone while driving — voice/single-tap mounted use only. "
        "Matters because employer liability attaches when crews drive between jobs on the clock; a "
        "written distracted-driving policy is the standard control.",
    "Cal. Lab. Code § 1400":
        "Cal/WARN's short-title section (post-AB 1601 renumbering) — it just names the act. The "
        "substance is in §1400.5 (definitions), §1401 (notice duty), and §1402 (liability), all "
        "captured as their own rows.",
    "Cal. Lab. Code § 1400.5":
        "Cal/WARN definitions: 'covered establishment' = 75+ employees (incl. part-time, 6 of last 12 "
        "months); 'mass layoff' = 50+ employees in 30 days; also defines relocation and termination. "
        "Much broader than federal WARN (no 1/3-of-workforce threshold).",
    "Cal. Lab. Code § 1401":
        "Cal/WARN's operative duty: 60 days' WRITTEN notice to affected employees, the EDD, the local "
        "workforce board, and local officials before a mass layoff, relocation, or plant closure at a "
        "covered establishment. Seasonal construction slowdowns have caused real Cal/WARN litigation — "
        "worth legal review before any large crew reduction.",
    "Cal. Lab. Code § 1402":
        "Cal/WARN liability: skip the notice and the employer owes each employee up to 60 days of back "
        "pay and benefits, plus civil penalties of $500/day. The cost of non-compliance usually dwarfs "
        "the cost of simply giving notice.",

    # ================= CA — EDD programs (PFL / SDI) =================
    "Cal. UIC § 3301 (PFL — EDD)":
        "Paid Family Leave: a state WAGE-REPLACEMENT benefit (not job protection) paying workers up to "
        "8 weeks at ~70–90% of wages to bond with a new child or care for a seriously ill family "
        "member. Funded entirely by employee SDI payroll deductions — costs the employer nothing. Job "
        "protection comes separately from CFRA. Employers must display/provide the EDD pamphlets.",
    "EDD — PFL benefit amounts":
        "The current PFL benefit math from EDD: weekly benefit ≈ 70–90% of the worker's highest "
        "quarter (higher % for lower earners, per SB 951), up to the annual maximum weekly benefit. "
        "These numbers change EVERY JANUARY — this row exists so the hash watcher catches the annual "
        "update automatically.",
    "Cal. UIC § 2601 (SDI — EDD)":
        "State Disability Insurance: the umbrella program (DI + PFL) paying partial wages when a "
        "worker can't work due to a NON-work illness, injury, or pregnancy (work injuries are workers' "
        "comp instead). Employee-funded via payroll withholding; employer duties are notice/poster and "
        "payroll deduction mechanics.",
    "EDD — DI benefit amounts":
        "The current Disability Insurance benefit math from EDD: ~70–90% wage replacement up to the "
        "annual cap, for up to 52 weeks. Updated annually — tracked by the hash watcher like the PFL "
        "amounts row.",
    "EDD — SDI/PFL contribution rates":
        "The employer-facing payroll mechanics: the current-year SDI withholding rate (the wage-base "
        "cap was removed in 2024 — the rate now applies to ALL wages), plus UI/ETT rates. This is what "
        "payroll must actually deduct; it changes every January 1.",

    # ================= CA — IWC Wage Order =================
    "IWC Wage Order 16-2001":
        "The Industrial Welfare Commission's wage order for ON-SITE CONSTRUCTION occupations — the "
        "industry-specific layer on top of the Labor Code that directly governs roofing crews: "
        "meal/rest period rules as applied on construction sites, daily/weekly overtime, alternative "
        "workweek schedules, reporting-time pay (half-day pay if sent home early), tool requirements, "
        "and record-keeping. Published only as a PDF (rev. 11/2025); we extract and watch the full "
        "text. Where a CBA meets the statutory tests, several provisions can be superseded.",
}


def coverage_check(citations):
    """Return the citations that have no explainer (so builds can warn)."""
    return sorted(c for c in citations if c not in EXPLAINERS)
