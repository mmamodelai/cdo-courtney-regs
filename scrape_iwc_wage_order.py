"""Scrape IWC Wage Order 16 (PDF) into compliance.regulations.

Wage Order 16-2001 regulates wages, hours and working conditions for ON-SITE
CONSTRUCTION occupations — it directly governs roofing crews (meal/rest periods,
daily/weekly overtime, reporting-time pay, makeup time, tools, rest facilities).
It's published only as a PDF on dir.ca.gov, so neither the leginfo nor the
Title 8 scraper can read it; this one extracts the text with pdfplumber.

One regulations row for the whole order (it amends as a unit; the content_hash
flags any revision — the form carries a "Rev. MM/YYYY" stamp).

Run:  python scrape_iwc_wage_order.py
"""
import io

import pdfplumber

from osha_common import (
    http_get, normalize_text, upsert_source, upsert_regulation, setup_schema,
)

PDF_URL = "https://www.dir.ca.gov/iwc/IWCArticle16.pdf"

IWC_SOURCE = {
    "name": "IWC Wage Orders (Wage Order 16 — construction)",
    "url": "https://www.dir.ca.gov/iwc/WageOrderIndustries.htm",
    "kind": "scrape",
    "jurisdiction": "CA",
    "notes": "Wage Order 16 governs on-site construction (meal/rest/OT for "
             "roofing). Scraped from the IWCArticle16.pdf via pdfplumber.",
}


def fetch_pdf_text(url: str) -> str:
    r = http_get(url)
    pages = []
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return normalize_text("\n".join(pages))


def main():
    setup_schema()
    print("IWC Wage Order 16 — on-site construction (PDF)")
    source_id = upsert_source(IWC_SOURCE)

    text = fetch_pdf_text(PDF_URL)
    if len(text) < 5000:
        raise RuntimeError(f"Wage Order 16 PDF extraction too short ({len(text)} chars) — "
                           "check the PDF layout or URL.")

    outcome = upsert_regulation({
        "jurisdiction": "CA",
        "topic": "wage_order",
        "title": "IWC Wage Order 16-2001 — on-site construction: wages, hours & working conditions",
        "citation": "IWC Wage Order 16-2001",
        "source_url": PDF_URL,
        "source_id": source_id,
        "raw_text": text,
        "domain": "wage_hour",
        "employee_count_min": 1,
        "industries": ["construction"],
        "applies_when": "on-site construction occupations (incl. roofing crews)",
    })
    print(f"  {outcome:9} IWC Wage Order 16-2001  [wage_order]  {len(text):,} chars")


if __name__ == "__main__":
    main()
