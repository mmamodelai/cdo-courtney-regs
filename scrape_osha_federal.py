"""Scrape Federal OSHA construction rules (29 CFR Part 1926) into compliance.regulations.

Uses the official eCFR versioner API, which returns authoritative current text as
structured XML — far more reliable than scraping the eCFR HTML (which bot-blocks).
One regulation row per CFR section listed in osha_sources.FEDERAL_SECTIONS.

Run:  python scrape_osha_federal.py
"""
from lxml import etree

from osha_common import (
    http_get, normalize_text, upsert_source, upsert_regulation, setup_schema,
)
from osha_sources import FEDERAL_SOURCE, FEDERAL_SECTIONS

ECFR_VERSIONS = "https://www.ecfr.gov/api/versioner/v1/versions/title-{title}.json"
ECFR_FULL = "https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml"
# Human-citable canonical URL (works in a browser; the API URL above is the fetch).
SECTION_URL = "https://www.ecfr.gov/current/title-{title}/section-{sec}"


def latest_issue_date(title: int = 29) -> str:
    """Ask eCFR for the most recent issue date of a CFR title (YYYY-MM-DD)."""
    meta = http_get(ECFR_VERSIONS.format(title=title)).json()["meta"]
    return meta["latest_issue_date"]


def fetch_section(date: str, section: str, title: int = 29):
    """Return (heading, full_text) for one CFR section, or None if missing."""
    part = section.split(".")[0]  # "1926.501" -> "1926"
    r = http_get(ECFR_FULL.format(date=date, title=title),
                 params={"part": part, "section": section})
    root = etree.fromstring(r.content)
    heading = (root.findtext(".//HEAD") or "").strip()
    if not heading:
        return None
    text = normalize_text(" ".join(t for t in root.itertext()))
    return heading, text


def main():
    setup_schema()
    date = latest_issue_date()
    print(f"Federal OSHA 29 CFR 1926 — eCFR text as of {date}")
    source_id = upsert_source(FEDERAL_SOURCE)

    tally = {"inserted": 0, "changed": 0, "unchanged": 0, "missing": 0}
    for section, topic, why in FEDERAL_SECTIONS:
        try:
            result = fetch_section(date, section)
        except Exception as e:
            print(f"  ! {section}: fetch error {e}")
            tally["missing"] += 1
            continue
        if result is None:
            print(f"  ! {section}: no content returned")
            tally["missing"] += 1
            continue
        heading, text = result
        # heading like "§ 1926.501 Duty to have fall protection." -> short name
        name = heading.split(" ", 2)[-1].strip().rstrip(".") if " " in heading else heading
        outcome = upsert_regulation({
            "jurisdiction": "Federal",
            "topic": topic,
            "title": f"29 CFR § {section} — {name}",
            "citation": f"29 CFR § {section}",
            "source_url": SECTION_URL.format(title=29, sec=section),
            "source_id": source_id,
            "raw_text": text,
        })
        tally[outcome] += 1
        print(f"  {outcome:9} 29 CFR § {section:9} [{topic}] {name[:60]}")

    print(f"\nFederal done: {tally}")


if __name__ == "__main__":
    main()
