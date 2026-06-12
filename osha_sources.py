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
    # --- General-industry standards incorporated by reference (added 2026-06-10):
    # 1926.59 and 1926.103 are one-line cross-references; the ACTUAL standards
    # live in Part 1910 (same Title 29, same eCFR API).
    ("1910.1200","hazcom",            "Hazard Communication — the full federal standard 1926.59 incorporates by reference"),
    ("1910.134", "respiratory_hazmat","Respiratory Protection — the full federal standard 1926.103 incorporates by reference"),
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
    ("1514",   "ppe",               "Personal protective devices — construction (points to GISO Art. 10)"),
    # NOTE (2026-06-10 audit): construction PPE §§1515/1516/1517/1520 are REPEALED
    # (eye/face repealed 2000; the GISO §3380-series governs construction too).
    # The current controlling PPE standards are the GISO Article 10 sections:
    ("3381",   "ppe",               "Head protection (GISO — current controlling standard)"),
    ("3382",   "ppe",               "Eye and face protection (GISO — current controlling standard)"),
    ("3383",   "ppe",               "Body protection (GISO)"),
    ("3384",   "ppe",               "Hand protection (GISO — current controlling standard)"),
    ("3385",   "ppe",               "Foot protection (GISO — current controlling standard)"),
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
