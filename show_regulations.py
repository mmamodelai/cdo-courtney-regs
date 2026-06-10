"""Quick read-only view of what's landed in compliance.regulations.

Run:  python show_regulations.py            (summary by jurisdiction/topic)
      python show_regulations.py 1926.501   (full row for one citation fragment)
"""
import sys

from db import get_conn


def overview():
    with get_conn() as c, c.cursor() as cur:
        cur.execute("select count(*) from compliance.regulations")
        print(f"compliance.regulations: {cur.fetchone()[0]} rows\n")
        cur.execute(
            "select jurisdiction, topic, count(*) "
            "from compliance.regulations group by 1,2 order by 1,2"
        )
        for j, t, n in cur.fetchall():
            print(f"  {j:8} {t:20} {n}")
        print()
        cur.execute(
            "select citation, title, length(raw_text) "
            "from compliance.regulations order by jurisdiction, citation"
        )
        for cit, title, n in cur.fetchall():
            print(f"  {cit:16} {n:7}c  {title[:70]}")


def detail(frag):
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "select citation, title, jurisdiction, topic, source_url, "
            "       content_hash, summary, raw_text "
            "from compliance.regulations where citation ilike %s limit 1",
            (f"%{frag}%",),
        )
        row = cur.fetchone()
    if not row:
        print(f"No regulation matching {frag!r}")
        return
    cit, title, jur, topic, url, h, summary, raw = row
    print(f"{cit}  [{jur} / {topic}]\n{title}\n{url}\nhash={h}\n")
    print("SUMMARY:", summary, "\n")
    print("RAW_TEXT (first 1200 chars):\n", raw[:1200])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        detail(sys.argv[1])
    else:
        overview()
