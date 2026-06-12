"""Scrape CA EDD program pages for PFL & SDI into compliance.regulations.

WHY EDD, not leginfo: PFL/SDI live in the CA Unemployment Insurance Code
(UIC §§ 2601+, 3300+), and leginfo's section view returns no
codeLawSectionNoHead container for UIC — the statute scraper can't read them.
EDD's program pages are the authoritative ADMINISTERED values anyway (benefit
percentages, max weekly amounts, contribution rates change annually), so we
scrape those and let the content_hash watcher flag the yearly updates.

Run:  python scrape_ca_edd.py
"""
import requests
from bs4 import BeautifulSoup

from osha_common import (
    HEADERS, normalize_text, upsert_source, upsert_regulation, setup_schema,
)

EDD_SOURCE = {
    "name": "CA EDD — PFL & SDI (benefit amounts & rates)",
    "url": "https://edd.ca.gov/en/disability/",
    "kind": "scrape",
    "jurisdiction": "CA",
    "notes": "PFL / SDI program rules, benefit amounts & contribution rates "
             "(UIC sections leginfo won't serve cleanly).",
}

# (url, topic, citation, name, applies_when)
EDD_PAGES = [
    ("https://edd.ca.gov/en/disability/paid-family-leave/",
     "pfl", "Cal. UIC § 3301 (PFL — EDD)",
     "Paid Family Leave — up to 8 weeks wage replacement (EDD program)",
     "employee on leave to care for family / bond with new child"),
    ("https://edd.ca.gov/en/disability/Calculating_PFL_Benefit_Payment_Amounts/",
     "pfl", "EDD — PFL benefit amounts",
     "PFL weekly benefit amounts — wage-replacement % and maximums (updated annually)",
     "employee on leave to care for family / bond with new child"),
    ("https://edd.ca.gov/en/disability/",
     "sdi", "Cal. UIC § 2601 (SDI — EDD)",
     "State Disability Insurance — program overview (DI + PFL umbrella)",
     "employee unable to work due to non-work illness/injury/pregnancy"),
    ("https://edd.ca.gov/en/disability/Calculating_DI_Benefit_Payment_Amounts/",
     "sdi", "EDD — DI benefit amounts",
     "DI weekly benefit amounts — wage-replacement % and maximums (updated annually)",
     "employee unable to work due to non-work illness/injury/pregnancy"),
    ("https://edd.ca.gov/en/payroll_taxes/rates_and_withholding/",
     "sdi", "EDD — SDI/PFL contribution rates",
     "SDI/PFL employee contribution rate & payroll-tax rates (updated annually)",
     "all CA employers — employee payroll withholding"),
]


def fetch_page(session, url):
    """Return normalized text of an EDD page's <main> content, or None."""
    r = session.get(url, timeout=60)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    body = soup.find("main") or soup.body
    if body is None:
        return None
    text = normalize_text(body.get_text("\n"))
    return text if len(text) > 200 else None


def main():
    setup_schema()
    print("CA EDD — PFL & SDI program pages")
    source_id = upsert_source(EDD_SOURCE)
    session = requests.Session()
    session.headers.update(HEADERS)

    tally = {"inserted": 0, "changed": 0, "unchanged": 0, "missing": 0}
    for url, topic, citation, name, applies_when in EDD_PAGES:
        try:
            text = fetch_page(session, url)
        except Exception as e:
            print(f"  ! {citation}: {e}")
            tally["missing"] += 1
            continue
        if text is None:
            print(f"  ! {citation}: no content")
            tally["missing"] += 1
            continue
        outcome = upsert_regulation({
            "jurisdiction": "CA",
            "topic": topic,
            "title": f"{citation} — {name}",
            "citation": citation,
            "source_url": url,
            "source_id": source_id,
            "raw_text": text,
            "domain": "leave_benefits",
            "employee_count_min": 1,
            "industries": ["all"],
            "applies_when": applies_when,
        })
        tally[outcome] += 1
        print(f"  {outcome:9} {citation:36} [{topic}] {name[:44]}")

    print(f"\nEDD done: {tally}")


if __name__ == "__main__":
    main()
