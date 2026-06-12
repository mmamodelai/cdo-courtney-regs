"""Quick read-only view of what's landed in compliance.regulations.

Run:  python show_regulations.py            (summary by jurisdiction/topic)
      python show_regulations.py 1926.501   (full row for one citation fragment)
"""
import sys
import db as _db


def overview():
    rows = _db._rpc("compliance_overview", {}) or []
    total = sum(r["cnt"] for r in rows)
    print(f"compliance.regulations: {total} rows\n")
    for r in rows:
        print(f"  {r['jurisdiction']:8} {r['topic']:20} {r['cnt']}")
    print()
    for r in (_db._rpc("compliance_fetch_regulations", {}) or []):
        title = r["title"]
        name = title.split(" — ", 1)[1] if " — " in title else title
        print(f"  {r['citation']:16} {r['chars']:7}c  {name[:70]}")


def detail(frag):
    rows = _db._rpc("compliance_get_one", {"p_frag": frag}) or []
    if not rows:
        print(f"No regulation matching {frag!r}")
        return
    r = rows[0]
    print(f"{r['citation']}  [{r['jurisdiction']} / {r['topic']}]\n{r['title']}\n{r['source_url']}\nhash={r['content_hash']}\n")
    print("SUMMARY:", r["summary"], "\n")
    print("RAW_TEXT (first 1200 chars):\n", (r["raw_text"] or "")[:1200])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        detail(sys.argv[1])
    else:
        overview()
