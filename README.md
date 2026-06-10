# CDO Compliance Scraper — Roof Tear-Off (Cal/OSHA + Federal OSHA)

Pulls the occupational-safety regulations that govern **roof tear-off / re-roofing**
work — California (Cal/OSHA Title 8) and Federal (OSHA 29 CFR Part 1926) — cleans
them, and lands them in the CDO database (the isolated `compliance` schema) with a
**citation + source_url on every row**. Provenance matters more than volume.

## Scope (what we watch)
Roofing-relevant hazard areas only — nothing wasteful:
fall protection · roofing operations · heat illness (CA §3395) · respiratory & hazmat
(asbestos, silica, lead, respirators) · PPE · materials handling / debris · ladders &
scaffolds. The exact, verified section list lives in **`osha_sources.py`** — that file
is the single source of truth for *what* we scrape. Add a row there to expand coverage;
no scraper code changes needed.

Current coverage: **36 sections** (20 federal, 16 California).

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python db.py                         # connection test — prints the 4 starter tables
```

### Connection note (important)
The direct DB host (`db.<ref>.supabase.co`) is deprecated and no longer resolves, so
`.env` uses the **Session pooler**. For the CDO project (region `us-east-1`) that is:
```
postgresql://compliance_intern.ruuufhxrubeckbcvwvcq:<password>@aws-1-us-east-1.pooler.supabase.com:5432/postgres
```
`python db.py` should print: `['documents', 'leave_rules', 'regulations', 'sources']`.

### One-time admin migration
The starter tables are owned by `postgres`, so the `compliance_intern` login has
insert/update/select but **cannot run DDL**. An admin must apply
**`migrations/001_watcher_keys.sql`** once (unique keys for idempotent upserts + a
`content_hash` column). Already applied to the CDO project on 2026-06-08.

## Run
```bash
python run_all.py                # both scrapers + a combined summary
# or individually:
python scrape_osha_federal.py    # Federal — 29 CFR 1926 via the official eCFR API
python scrape_calosha_title8.py  # California — Title 8 via dir.ca.gov
python show_regulations.py       # read-only: what's landed, by jurisdiction/topic
python show_regulations.py 1926.501   # full detail for one citation
```
Re-running is **safe and idempotent**: rows upsert by `citation`, so you get inserts
for new sections and updates for changed text — never duplicates. Each run reports
`inserted / changed / unchanged`, which is the seed of the change-detection watcher.

## Files
| File | Role |
|---|---|
| `osha_sources.py` | Verified source + section lists (the "what"). Edit to expand. |
| `osha_common.py` | DB upserts, text normalization, SHA-256 hashing, schema check. |
| `scrape_osha_federal.py` | Federal eCFR API scraper (29 CFR 1926). |
| `scrape_calosha_title8.py` | Cal/OSHA Title 8 HTML scraper (dir.ca.gov). |
| `run_all.py` | Runs every scraper; the future cron entry point. |
| `show_regulations.py` | Read-only inspector. |
| `migrations/001_watcher_keys.sql` | Admin-run schema prep. |
| `db.py` | Connection helper + schema introspection. |
| `scrape_ca_pfl.py` | Original leave-rules starter template (kept for reference). |

## How data is stored
| Table | For |
|---|---|
| `compliance.sources` | each agency/source scraped, with `last_scraped_at` |
| `compliance.regulations` | one rule/section — `citation` + `source_url` + `content_hash` + full `raw_text` |

## What's next (not built yet — "land data first")
A scheduled **watcher**: run `run_all.py` on a cron, and on any `changed` outcome log
a change row / send a digest. The `content_hash` column and the per-run
`inserted/changed/unchanged` tally already make this a thin add-on. Also pending:
roofing-relevant local ordinances and CSLB C-39 licensing (placeholders in the M2
source inventory).
