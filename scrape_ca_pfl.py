"""Starter scraper: California Paid Family Leave → compliance.regulations.

This is a TEMPLATE. It registers the source and inserts a couple of hand-entered
PFL facts so you can see the pattern. Your job: replace ROWS with content actually
scraped from the EDD site, with real citations + effective dates.

Source: https://edd.ca.gov/en/disability/paid-family-leave/
Pattern: 1) register the source, 2) insert regulation rows with citation + source_url.
"""
from db import get_conn

SOURCE = {
    "name": "CA EDD — Paid Family Leave",
    "url": "https://edd.ca.gov/en/disability/paid-family-leave/",
    "kind": "agency",
    "jurisdiction": "CA",
}

# TODO(Courtney): replace these starters with scraped, dated content.
ROWS = [
    {
        "jurisdiction": "CA",
        "topic": "paid_family_leave",
        "title": "Paid Family Leave — benefit duration",
        "summary": "Up to 8 weeks of PFL benefits within any 12-month period.",
        "citation": "Cal. Unemp. Ins. Code § 3301",
        "source_url": SOURCE["url"],
        "status": "draft",
    },
]


def main():
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "insert into compliance.sources (name, url, kind, jurisdiction, last_scraped_at) "
            "values (%(name)s, %(url)s, %(kind)s, %(jurisdiction)s, now()) returning id",
            SOURCE,
        )
        source_id = cur.fetchone()[0]
        for r in ROWS:
            r["source_id"] = source_id
            cur.execute(
                "insert into compliance.regulations "
                "(jurisdiction, topic, title, summary, citation, source_url, status, source_id) "
                "values (%(jurisdiction)s, %(topic)s, %(title)s, %(summary)s, %(citation)s, "
                "%(source_url)s, %(status)s, %(source_id)s)",
                r,
            )
        print(f"Inserted {len(ROWS)} regulation row(s) under source {source_id}.")


if __name__ == "__main__":
    main()
