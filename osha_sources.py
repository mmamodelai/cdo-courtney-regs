"""Verified regulation sources for ROOF TEAR-OFF compliance (CA + Federal).

This is the single source of truth for WHAT we scrape. Every section below was
verified to resolve live (Federal via the eCFR API, California via dir.ca.gov)
on 2026-06-08. To expand coverage, add rows here — the scrapers are generic and
read from this file, so no scraper code needs to change.

Scope: occupational-safety regulations relevant to roof tear-off / re-roofing
work — fall protection, roofing operations, heat, respiratory & hazmat exposure
(asbestos / silica / lead common when stripping old roofs), PPE, materials
handling/debris, ladders & scaffolds. Intentionally narrow: only sections a
roofing crew or its safety officer actually needs.

`topic` values are shared across jurisdictions so a federal rule and its CA
counterpart group together: fall_protection, roofing_ops, heat_illness,
respiratory_hazmat, hazcom, ppe, materials_handling, ladders, scaffolds.
"""

# ---------------------------------------------------------------------------
# FEDERAL — OSHA 29 CFR Part 1926 (Construction). Pulled from the eCFR API.
# ---------------------------------------------------------------------------
FEDERAL_SOURCE = {
    "name": "Federal OSHA — 29 CFR Part 1926 (Construction Safety & Health)",
    "url": "https://www.ecfr.gov/current/title-29/part-1926",
    "kind": "api",            # eCFR versioner API (authoritative current text)
    "jurisdiction": "Federal",
    "notes": "Source of record for the federal floor. Heat has no specific 1926 "
             "standard yet (covered by OSH Act Gen. Duty Clause 5(a)(1); a federal "
             "heat rule was proposed in 2024 but is not in the CFR).",
}

# (section, topic, why-it-matters-for-roof-tear-off)
FEDERAL_SECTIONS = [
    ("1926.500", "fall_protection",   "Subpart M scope & definitions for fall protection"),
    ("1926.501", "fall_protection",   "Duty to have fall protection (incl. (b)(10) low-slope roofing)"),
    ("1926.502", "fall_protection",   "Fall protection systems criteria (guardrails, PFAS, warning lines)"),
    ("1926.503", "fall_protection",   "Fall protection training requirements"),
    ("1926.95",  "ppe",               "Criteria for personal protective equipment"),
    ("1926.96",  "ppe",               "Occupational foot protection"),
    ("1926.100", "ppe",               "Head protection (hard hats)"),
    ("1926.101", "ppe",               "Hearing protection"),
    ("1926.102", "ppe",               "Eye and face protection"),
    ("1926.103", "respiratory_hazmat","Respiratory protection (adopts 1910.134)"),
    ("1926.55",  "respiratory_hazmat","Gases, vapors, fumes, dusts & mists exposure limits"),
    ("1926.62",  "respiratory_hazmat","Lead — old roof flashing/coatings disturbed in tear-off"),
    ("1926.1101","respiratory_hazmat","Asbestos — common in legacy roofing/mastic on tear-off"),
    ("1926.1153","respiratory_hazmat","Respirable crystalline silica — tile/concrete/cutting"),
    ("1926.59",  "hazcom",            "Hazard communication (adopts 1910.1200)"),
    ("1926.250", "materials_handling","General storage requirements (staging materials on roof)"),
    ("1926.252", "materials_handling","Disposal of waste materials (debris chutes during tear-off)"),
    ("1926.451", "scaffolds",         "Scaffold general requirements (access/landing)"),
    ("1926.1051","ladders",           "Stairways & ladders — general access"),
    ("1926.1053","ladders",           "Ladders (roof access)"),
]

# ---------------------------------------------------------------------------
# CALIFORNIA — Cal/OSHA Title 8 (Construction Safety Orders + General Industry
# Safety Orders). Scraped from dir.ca.gov. Decimal sections use an underscore in
# the filename (e.g. 1532.1 -> 1532_1.html); the scraper handles that mapping.
# ---------------------------------------------------------------------------
CALIFORNIA_SOURCE = {
    "name": "Cal/OSHA — Title 8 (Construction & General Industry Safety Orders)",
    "url": "https://www.dir.ca.gov/title8/",
    "kind": "scrape",
    "jurisdiction": "CA",
    "notes": "California is stricter than the federal floor: it has a dedicated "
             "roofing article and a specific Heat Illness standard (§3395).",
}

# (section, topic, why-it-matters-for-roof-tear-off)
CALIFORNIA_SECTIONS = [
    ("1669",   "fall_protection",   "Fall protection — general (Article 24)"),
    ("1670",   "fall_protection",   "Personal fall arrest / restraint / positioning devices"),
    ("1671",   "fall_protection",   "Safety nets"),
    ("1724",   "roofing_ops",       "Roofing — general (Article 29)"),
    ("1730",   "roofing_ops",       "Roof hazards (slope, openings, edges)"),
    ("1731",   "roofing_ops",       "Residential-type roofing activities"),
    ("3395",   "heat_illness",      "Heat illness prevention in outdoor places of employment"),
    ("1529",   "respiratory_hazmat","Asbestos (construction)"),
    ("1532.1", "respiratory_hazmat","Lead (construction)"),
    ("1532.3", "respiratory_hazmat","Respirable crystalline silica (construction)"),
    ("5144",   "respiratory_hazmat","Respiratory protective equipment"),
    ("1514",   "ppe",               "Personal protective devices — general"),
    ("1515",   "ppe",               "Head protection"),
    ("1516",   "ppe",               "Eye and face protection"),
    ("1517",   "ppe",               "Foot protection"),
    ("1520",   "ppe",               "Hand protection"),
    # --- Critical-30 safety completeness (added 2026-06-09) ---
    ("3203",   "safety_program",    "Injury & Illness Prevention Program (IIPP) — the foundational CA safety program every employer must have"),
    ("5194",   "hazcom",            "Hazard Communication (CA controlling standard; construction provisions at (f)(7); adds Prop 65)"),
    ("3314",   "lockout_tagout",    "Control of Hazardous Energy (Lockout/Tagout) — powered equipment service/repair"),
    ("3221",   "fire_safety",       "Fire Prevention Plan"),
    ("3400",   "first_aid",         "Medical Services and First Aid (incl. CPR readiness)"),
    ("3380",   "ppe",               "Personal Protective Devices (GISO) — the §3380 citation the Critical-30 references; complements construction PPE §1514–1520"),
    # Confined space: use the CONSTRUCTION standard (Article 37), per the 2026-06-09
    # audit. General-industry §5157 is NOT controlling for construction work.
    ("1950",   "confined_space",    "Confined Spaces in Construction — Article 37 scope (§§1950–1962); supersedes general-industry §5157 for construction"),
]
