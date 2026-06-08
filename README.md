# CDO Compliance Scraper

Pull California / federal compliance + leave regulations, clean them, and land them
in the CDO database (the isolated `compliance` schema). Reference data the company
uses for docs, forms, and policy.

## Setup (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# .env is already provided (see CONNECTION.md). Do not commit it.
python db.py          # connection test — prints the 4 starter tables
python scrape_ca_pfl.py   # runs the starter template
```

## Working with Claude Code
- Launch Claude Code **in this folder**.
- Have it read `CONNECTION.md` and `db.py` first — that's the access pattern + the rules.
- Before writing inserts, ask it to introspect the live schema:
  > "use db.columns() to show the columns of compliance.regulations and compliance.leave_rules"
- It can only reach the `compliance` schema — by design. Nothing else in CDO is exposed to this login.

## What goes where
| Table | For |
|---|---|
| `compliance.sources` | each site/agency you scraped, with last_scraped_at |
| `compliance.regulations` | a regulation/requirement, with **citation + source_url** |
| `compliance.leave_rules` | CA PFL/CFRA/FMLA/sick specifics (entitlement, pay %, eligibility) |
| `compliance.documents` | forms / posters / policies to maintain |

You can create more tables in the `compliance` schema anytime. See `CONNECTION.md`.
