"""Register the FULL regulatory source watch-list (Master Plan §11) in compliance.sources.

This is the "Verified regulatory-source inventory" deliverable (M2): every official
source the watcher should monitor — federal, California, and industry — with its URL
and watch method. Sources we already scrape full text from are status='active';
the rest are status='registered' (watch-list / future scrape or watcher-only feed).

Idempotent: keyed on url. Does NOT clobber the status / last_scraped_at of the
sources our scrapers already manage.

Run:  python register_sources.py
"""
from db import get_conn

# (name, url, kind, jurisdiction, status, notes)
SOURCES = [
    # ---------- FEDERAL ----------
    ("Federal eCFR — 29 CFR (labor & employment)", "https://www.ecfr.gov/current/title-29",
     "api", "Federal", "active",
     "eCFR API (no key). Authoritative current text: OSHA 1926, FMLA 825, FLSA 541/778, ADA 1630, Title VII 1604."),
    ("Federal Register — rules & proposed rules (API)", "https://www.federalregister.gov/developers/api/v1",
     "api", "Federal", "registered",
     "JSON, no auth. System of record for federal rule CHANGES; filter agency=OSHA/DOL/EEOC; de-dup by FR document number."),
    ("OSHA — News Releases", "https://www.osha.gov/news/newsreleases.xml",
     "rss", "Federal", "registered", "RSS feed for OSHA enforcement/guidance news."),
    ("US DOL Wage & Hour Division — news", "https://www.dol.gov/agencies/whd/news",
     "rss", "Federal", "registered", "FLSA/FMLA enforcement & guidance updates."),
    ("EEOC — Press Releases", "https://www.eeoc.gov/newsroom/press-releases",
     "rss", "Federal", "registered", "Title VII / ADA / EEO enforcement & guidance."),
    ("US DOL — FMLA", "https://www.dol.gov/agencies/whd/fmla",
     "scrape", "Federal", "registered", "FMLA guidance, fact sheets, posters."),
    ("Regulations.gov — dockets & comments (API)", "https://api.regulations.gov/v4",
     "api", "Federal", "registered", "Needs api.data.gov key (stored in .env). Proposed-rule dockets."),
    ("Congress.gov — federal statutes (API)", "https://api.congress.gov/v3",
     "api", "Federal", "registered", "Needs Congress key (stored in .env). Enacted/amended labor statutes."),
    # ---------- CALIFORNIA ----------
    ("Cal/OSHA — Title 8 (dir.ca.gov)", "https://www.dir.ca.gov/title8/",
     "scrape", "CA", "active", "Construction + General Industry Safety Orders — full text scraped."),
    ("California statutes — leginfo (Labor/Gov/B&P)", "https://leginfo.legislature.ca.gov/faces/codesTOCSelected.xhtml?tocCode=LAB",
     "scrape", "CA", "active", "Wage/hour, leave, harassment, licensing, prevailing wage — full statute text scraped."),
    ("Cal/OSHA Standards Board — rulemaking", "https://www.dir.ca.gov/oshsb/oshsb.html",
     "scrape", "CA", "registered", "Proposed/approved CA safety standards + hearing agendas (leading indicator of change)."),
    ("CA EDD — news & benefit amounts", "https://edd.ca.gov/en/about_edd/news_releases/",
     "scrape", "CA", "registered", "PFL / SDI benefit amounts & news (UIC sections leginfo won't serve cleanly)."),
    ("CA Civil Rights Department (CRD / DFEH)", "https://calcivilrights.ca.gov/news",
     "scrape", "CA", "registered", "FEHA / CFRA / PDL regulations & guidance."),
    ("CalChamber — HR Watchdog", "https://www.calchamber.com/hrwatchdog",
     "subscription", "CA", "registered", "PAID feed — no scraping; secondary signal only."),
    ("IWC Wage Orders (Wage Order 16 — construction)", "https://www.dir.ca.gov/iwc/WageOrderIndustries.htm",
     "scrape", "CA", "registered", "Wage Order 16 governs on-site construction (meal/rest/OT for roofing). PDF — needs PDF parse."),
    ("CSLB — Contractors State License Board", "https://www.cslb.ca.gov",
     "scrape", "CA", "registered", "C-39 roofing license + bond requirements & disciplinary rule changes."),
    # ---------- INDUSTRY ----------
    ("NRCA — National Roofing Contractors Assoc.", "https://www.nrca.net",
     "scrape", "Industry", "registered", "ROOFING — newsletter + standards/best practices (our launch industry)."),
    ("ABC — Associated Builders & Contractors", "https://www.abc.org",
     "scrape", "Industry", "registered", "Construction (general) — safety council updates."),
    ("PHCC — Plumbing-Heating-Cooling Contractors", "https://www.phccweb.org",
     "scrape", "Industry", "registered", "Plumbing — future industry (not active for roofing)."),
    ("ACCA — Air Conditioning Contractors", "https://www.acca.org",
     "scrape", "Industry", "registered", "HVAC — future industry (not active for roofing)."),
    ("IAPMO — Uniform Plumbing Code", "https://www.iapmo.org",
     "scrape", "Industry", "registered", "Plumbing — future industry (not active for roofing)."),
]


def main():
    inserted = updated = 0
    with get_conn() as c, c.cursor() as cur:
        for name, url, kind, jur, status, notes in SOURCES:
            # Preserve status/last_scraped_at for sources our scrapers manage:
            # set status only on INSERT; on conflict refresh metadata but keep status.
            cur.execute("select 1 from compliance.sources where url=%s", (url,))
            exists = cur.fetchone() is not None
            cur.execute(
                "insert into compliance.sources (name, url, kind, jurisdiction, status, notes) "
                "values (%s,%s,%s,%s,%s,%s) "
                "on conflict (url) do update set name=excluded.name, kind=excluded.kind, "
                "  jurisdiction=excluded.jurisdiction, notes=excluded.notes",
                (name, url, kind, jur, status, notes),
            )
            updated += exists
            inserted += not exists
    print(f"Source watch-list registered: {inserted} new, {updated} refreshed.")
    with get_conn() as c, c.cursor() as cur:
        cur.execute("select jurisdiction, count(*), "
                    "count(*) filter (where status='active') "
                    "from compliance.sources group by 1 order by 1")
        for jur, n, active in cur.fetchall():
            print(f"  {jur:9} {n} sources ({active} active / {n-active} registered)")


if __name__ == "__main__":
    main()
