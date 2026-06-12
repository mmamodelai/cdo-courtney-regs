"""Scrape Cal/OSHA Title 8 sections (dir.ca.gov) into compliance.regulations.

California Code of Regulations, Title 8 — Construction Safety Orders + the General
Industry Safety Orders that apply to roof work (heat, respirators, PPE). One
regulation row per section listed in osha_sources.CALIFORNIA_SECTIONS.

dir.ca.gov serves one stable HTML page per section. Decimal sections use an
underscore in the filename (1532.1 -> 1532_1.html). The real regulation text sits
after a fixed nav/disclaimer header that ends right before the "§<section>."
marker, so we slice from there and drop residual nav lines.

Run:  python scrape_calosha_title8.py
"""
import re

from bs4 import BeautifulSoup

from osha_common import (
    http_get, normalize_text, upsert_source, upsert_regulation, setup_schema,
)
from osha_sources import CALIFORNIA_SOURCE, CALIFORNIA_SECTIONS

PAGE = "https://www.dir.ca.gov/title8/{file}.html"

# Nav / disclaimer junk that can appear around the real text.
_JUNK = re.compile(
    r"(skip to main content|information is provided free of charge|convenience of the user"
    r"|is current or accurate|see full disclaimer|disclaimer\.html|return to index"
    r"|new query|go back to|www\.dir\.ca\.gov)",
    re.I,
)


def section_file(section: str) -> str:
    """1532.1 -> 1532_1 ; 1670 -> 1670."""
    return section.replace(".", "_")


def official_name(soup: BeautifulSoup, section: str) -> str:
    """Pull the section name from <title>: '... Section 1670. <name>.'"""
    # Collapse internal whitespace first — some titles (e.g. §3314) span lines.
    title = re.sub(r"\s+", " ", (soup.title.string if soup.title else "") or "").strip()
    m = re.search(rf"Section\s+{re.escape(section)}\.\s*(.+?)\.?\s*$", title)
    return m.group(1).strip() if m else title


def clean_text(soup: BeautifulSoup, section: str) -> str:
    """Return the regulation body, from the '§<section>.' marker onward, denoised."""
    full = soup.get_text("\n", strip=True)
    # find the section marker line: "§1670." / "§ 1670." / "1670."
    marker = re.search(rf"(?m)^\s*§?\s*{re.escape(section)}\.", full)
    body = full[marker.start():] if marker else full
    lines = [ln.strip() for ln in body.splitlines()]
    kept = [ln for ln in lines if ln and not _JUNK.search(ln)]
    return normalize_text("\n".join(kept))


def main():
    setup_schema()
    print("Cal/OSHA — Title 8 (dir.ca.gov)")
    source_id = upsert_source(CALIFORNIA_SOURCE)

    tally = {"inserted": 0, "changed": 0, "unchanged": 0, "missing": 0}
    for section, topic, why in CALIFORNIA_SECTIONS:
        url = PAGE.format(file=section_file(section))
        try:
            r = http_get(url)
        except Exception as e:
            print(f"  ! {section}: fetch error {e}")
            tally["missing"] += 1
            continue
        soup = BeautifulSoup(r.text, "lxml")
        name = official_name(soup, section)
        if "404" in (soup.title.string or "") if soup.title else False:
            print(f"  ! {section}: 404")
            tally["missing"] += 1
            continue
        text = clean_text(soup, section)
        if len(text) < 40:
            print(f"  ! {section}: text too short ({len(text)} chars) — skipped")
            tally["missing"] += 1
            continue
        # Repeal guard (2026-06-10): dir.ca.gov keeps shell pages for repealed
        # sections — '§1516. Eye and Face Protection. (Repealed)' + HISTORY only.
        # A repealed section is NOT law; never store it as a Tier-1 fact.
        if re.match(rf"§?\s*{re.escape(section)}\.[^\n]{{0,120}}[(\[]\s*Repealed\s*[)\]]",
                    text, re.I):
            print(f"  !! {section}: REPEALED on dir.ca.gov — skipped. "
                  f"Remove it from osha_sources.py and find the current standard.")
            tally["missing"] += 1
            continue
        outcome = upsert_regulation({
            "jurisdiction": "CA",
            "topic": topic,
            "title": f"8 CCR § {section} — {name}",
            "citation": f"8 CCR § {section}",
            "source_url": url,
            "source_id": source_id,
            "raw_text": text,
        })
        tally[outcome] += 1
        print(f"  {outcome:9} 8 CCR § {section:7} [{topic}] {name[:60]}")

    print(f"\nCalifornia done: {tally}")


if __name__ == "__main__":
    main()
