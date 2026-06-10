"""Scrape FEDERAL employment-law regulations (29 CFR) into compliance.regulations.

The federal floor beyond OSHA construction: FMLA, FLSA, ADA, Title VII. All live in
Title 29 of the CFR, so we reuse the eCFR API (same reliable path as the OSHA 1926
scraper — no key, authoritative current text).

Federal thresholds are important applicability DATA: FMLA applies at 50+ employees,
ADA / Title VII at 15+, FLSA at any size. These sit alongside CA's 5/25 triggers so
the engine can resolve federal-vs-state coverage per client.

Run:  python scrape_fed_employment.py
"""
from scrape_osha_federal import latest_issue_date, fetch_section, SECTION_URL
from osha_common import upsert_source, upsert_regulation, setup_schema

FED_EMPLOYMENT_SOURCE = {
    "name": "Federal eCFR — 29 CFR (labor & employment)",
    "url": "https://www.ecfr.gov/current/title-29",
    "kind": "api",
    "jurisdiction": "Federal",
    "notes": "eCFR API (no key). Federal employment floor: FMLA 825, FLSA 541/778, "
             "ADA 1630, Title VII 1604.",
}

# (section, domain, topic, name, applies_when, employee_count_min)
FED_EMPLOYMENT = [
    # FMLA — 29 CFR 825 (50+ employees within 75 miles)
    ("825.100", "leave_benefits", "fmla", "FMLA — general / the Act in a nutshell", "50+ employees within 75 miles", 50),
    ("825.200", "leave_benefits", "fmla", "FMLA — amount of leave (12 workweeks)",  "50+ employees within 75 miles", 50),
    ("825.112", "leave_benefits", "fmla", "FMLA — qualifying reasons for leave",     "50+ employees within 75 miles", 50),
    # FLSA — overtime & exemptions (any size)
    ("778.107", "wage_hour", "flsa_overtime", "FLSA — general overtime pay standard (1.5× after 40h/week)", None, 1),
    ("541.100", "wage_hour", "flsa_exempt",   "FLSA — executive exemption (white-collar test)",             None, 1),
    # ADA — 29 CFR 1630 (15+ employees)
    ("1630.2", "harassment_eeo", "ada", "ADA — definitions (disability, reasonable accommodation, undue hardship)", "15+ employees", 15),
    ("1630.9", "harassment_eeo", "ada", "ADA — reasonable accommodation & not making accommodation",               "15+ employees", 15),
    # Title VII — 29 CFR 1604 (15+ employees)
    ("1604.11", "harassment_eeo", "title_vii", "Title VII — sexual harassment guidelines", "15+ employees", 15),
]


def main():
    setup_schema()
    date = latest_issue_date()
    print(f"Federal employment law — 29 CFR via eCFR (as of {date})")
    source_id = upsert_source(FED_EMPLOYMENT_SOURCE)

    tally = {"inserted": 0, "changed": 0, "unchanged": 0, "missing": 0}
    for section, domain, topic, name, applies_when, min_emp in FED_EMPLOYMENT:
        try:
            result = fetch_section(date, section)
        except Exception as e:
            print(f"  ! {section}: fetch error {e}")
            tally["missing"] += 1
            continue
        if result is None:
            print(f"  ! {section}: no content")
            tally["missing"] += 1
            continue
        _, text = result
        outcome = upsert_regulation({
            "jurisdiction": "Federal",
            "topic": topic,
            "title": f"29 CFR § {section} — {name}",
            "citation": f"29 CFR § {section}",
            "source_url": SECTION_URL.format(sec=section),
            "source_id": source_id,
            "raw_text": text,
            "domain": domain,
            "employee_count_min": min_emp,
            "industries": ["all"],
            "applies_when": applies_when,
        })
        tally[outcome] += 1
        print(f"  {outcome:9} 29 CFR § {section:9} [{domain}] {name[:46]}")

    print(f"\nFederal employment done: {tally}")


if __name__ == "__main__":
    main()
