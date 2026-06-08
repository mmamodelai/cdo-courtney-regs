# CDO Compliance Scraper — Database Access

## What you have
A **scoped** Postgres login that can do anything inside **one schema — `compliance`** —
and nothing else in the CDO database. Employee, payroll, and customer data are *not*
reachable with this login. That's intentional and good.

## `compliance` is a SCHEMA, not a table
Think of `compliance` as a labeled **drawer** that holds many tables. Your tables live inside it:

- `compliance.sources` — where you scraped each thing from
- `compliance.regulations` — regulation lookups (jurisdiction, topic, citation, source_url…)
- `compliance.leave_rules` — CA PFL / CFRA / FMLA / paid sick (entitlement, pay %, eligibility…)
- `compliance.documents` — forms / policies / posters to maintain

You can **create / alter / drop your own tables** inside this drawer freely, e.g.:
```sql
create table compliance.ca_required_posters (id bigint generated always as identity primary key, name text, url text);
```
You just can't reach anything *outside* `compliance`.

## Connect
Your connection string is in `.env` (already created — **never commit it**). Test it:
```bash
python db.py        # should print the 4 starter tables
```

### If it won't connect (network has no IPv6)
Supabase deprecated direct IPv4. Get the **Session pooler** string from the Supabase
dashboard → **Connect** → "Session pooler", then in `.env` set the user to
`compliance_intern.ruuufhxrubeckbcvwvcq` and keep the same password. Done.

## Rules
- Work only in the `compliance` schema (it's all you can touch anyway).
- **Never commit `.env`.**
- On every regulation row, include a `source_url` **and** a `citation` — this is
  compliance data; provenance matters more than volume.
- For anything outside `compliance`, or production access, ask Stephen or Aaron.
