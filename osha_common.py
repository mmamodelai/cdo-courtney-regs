"""Shared helpers for the OSHA roof tear-off scrapers.

Keeps the two scrapers (federal eCFR + Cal/OSHA Title 8) thin: they just fetch &
parse, then hand normalized rows to `upsert_regulation` here. Everything is
idempotent — re-running a scraper updates existing rows instead of duplicating,
which is what makes "continuously scraped" safe to run on a schedule.
"""
import re
import hashlib
import datetime as _dt

import requests

from db import get_conn

UA = "CDO-compliance-scraper/1.0 (+https://github.com/mmamodelai/CDO-compliance-scraper; team@mmamodel.ai)"
HEADERS = {"User-Agent": UA}
TIMEOUT = 60


def http_get(url, **kwargs):
    """GET with our identifying User-Agent and a sane timeout. Raises on != 2xx."""
    kwargs.setdefault("headers", HEADERS)
    kwargs.setdefault("timeout", TIMEOUT)
    r = requests.get(url, **kwargs)
    r.raise_for_status()
    return r


def normalize_text(text: str) -> str:
    """Collapse whitespace so a trivial reformat doesn't look like a real change.

    Used both for the stored `raw_text` and as the input to `content_hash`, so the
    hash tracks substantive content, not spacing.
    """
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def content_hash(text: str) -> str:
    """SHA-256 of normalized text — the change-detection signal for the watcher."""
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def make_summary(text: str, limit: int = 320) -> str:
    """A short human-readable blurb: the first substantive sentence(s)."""
    flat = re.sub(r"\s+", " ", text).strip()
    if len(flat) <= limit:
        return flat
    cut = flat[:limit]
    dot = cut.rfind(". ")
    return (cut[: dot + 1] if dot > 80 else cut).strip() + " …"


# ---------------------------------------------------------------------------
# Schema prerequisites. The compliance_intern login has DML only — it cannot run
# DDL (the starter tables are owned by postgres). So the unique keys + content_hash
# column are installed once by an admin via migrations/001_watcher_keys.sql. Here we
# just verify they exist and fail with a clear instruction if they don't.
# ---------------------------------------------------------------------------
class MigrationMissing(RuntimeError):
    pass


def setup_schema():
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "select 1 from pg_constraint where conname = 'regulations_citation_key'"
        )
        has_key = cur.fetchone() is not None
        cur.execute(
            "select 1 from information_schema.columns "
            "where table_schema='compliance' and table_name='regulations' "
            "and column_name='content_hash'"
        )
        has_col = cur.fetchone() is not None
    if not (has_key and has_col):
        raise MigrationMissing(
            "Required schema is missing. An admin must apply "
            "migrations/001_watcher_keys.sql once (compliance_intern lacks DDL "
            "rights on the postgres-owned tables)."
        )


def upsert_source(source: dict) -> int:
    """Insert/update a compliance.sources row keyed on url; return its id."""
    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "insert into compliance.sources "
            "  (name, url, kind, jurisdiction, status, notes, last_scraped_at) "
            "values (%(name)s, %(url)s, %(kind)s, %(jurisdiction)s, 'active', %(notes)s, now()) "
            "on conflict (url) do update set "
            "  name = excluded.name, kind = excluded.kind, "
            "  jurisdiction = excluded.jurisdiction, notes = excluded.notes, "
            "  last_scraped_at = now() "
            "returning id",
            {"notes": None, **source},
        )
        return cur.fetchone()[0]


# ---------------------------------------------------------------------------
# Applicability — modeled as DATA so the onboarding engine can filter per client
# (employee count × industry × trigger condition), not assume one company.
# Derived from topic + citation if a row doesn't supply its own. As we add more
# compliance domains, scrapers can pass domain/employee_count_min/etc. explicitly.
# ---------------------------------------------------------------------------
TOPIC_DOMAIN = {  # every current topic is a safety standard
    "fall_protection": "safety", "roofing_ops": "safety", "heat_illness": "safety",
    "respiratory_hazmat": "safety", "ppe": "safety", "materials_handling": "safety",
    "ladders": "safety", "scaffolds": "safety", "hazcom": "safety",
    "safety_program": "safety", "lockout_tagout": "safety", "fire_safety": "safety",
    "first_aid": "safety", "confined_space": "safety",
    # wage & hour
    "overtime": "wage_hour", "meal_rest": "wage_hour", "wage_statements": "wage_hour",
    "final_pay": "wage_hour", "minimum_wage": "wage_hour", "wage_notice": "wage_hour",
    # leave & benefits
    "paid_sick_leave": "leave_benefits", "family_medical_leave": "leave_benefits",
    "bereavement_leave": "leave_benefits", "civic_leave": "leave_benefits",
    # harassment / EEO / violence
    "discrimination": "harassment_eeo", "harassment_training": "harassment_eeo",
    "workplace_violence": "harassment_eeo",
    # licensing / insurance / prevailing wage
    "workers_comp": "licensing_insurance", "contractor_license": "licensing_insurance",
    "prevailing_wage": "prevailing_wage",
    # federal employment law
    "fmla": "leave_benefits", "flsa_overtime": "wage_hour", "flsa_exempt": "wage_hour",
    "ada": "harassment_eeo", "title_vii": "harassment_eeo",
    # additional employer obligations
    "expense_reimbursement": "wage_hour", "day_of_rest": "wage_hour",
    "pay_transparency": "wage_hour", "personnel_records": "wage_hour",
    "lactation": "leave_benefits", "military_leave": "leave_benefits",
    "fair_chance": "harassment_eeo", "whistleblower": "harassment_eeo",
    "ab5": "worker_classification", "calsavers": "benefits_retirement",
    "social_media": "privacy_conduct", "trade_secrets": "privacy_conduct",
    "distracted_driving": "privacy_conduct", "warn_act": "workforce_reduction",
}

# Trigger condition keyed by a citation fragment; absence => generally applicable.
APPLIES_WHEN = {
    "3395": "outdoor work / high-heat conditions",
    "1532.3": "cutting/grinding/disturbing silica-containing materials",
    "1926.1153": "cutting/grinding/disturbing silica-containing materials",
    "1529": "disturbing asbestos-containing materials (common in tear-off)",
    "1926.1101": "disturbing asbestos-containing materials (common in tear-off)",
    "1532.1": "disturbing lead-containing materials/coatings",
    "1926.62": "disturbing lead-containing materials/coatings",
    "1950": "entry into a confined space",
    "3314": "servicing/maintaining powered equipment",
    "1926.451": "scaffold use on site",
    "1926.1053": "ladder use on site", "1926.1051": "ladder/stairway use on site",
    "5144": "respirator use required by another standard",
    "1926.103": "respirator use required by another standard",
}


def _industries_for(citation: str):
    """29 CFR 1926 + CA Title 8 §1500–1999 = construction; GISO (3000s/5000s) = all."""
    m = re.search(r"(\d+)", citation)
    if citation.startswith("29 CFR"):
        return ["construction"]
    if m and 1500 <= int(m.group(1)) < 2000:
        return ["construction"]
    return ["all"]


def _applies_when_for(citation: str):
    for frag, cond in APPLIES_WHEN.items():
        if frag in citation:
            return cond
    return None


def upsert_regulation(reg: dict) -> str:
    """Insert/update a compliance.regulations row keyed on citation.

    Returns one of: 'inserted', 'changed', 'unchanged' — so the run summary can
    report what actually moved (the seed of change detection).
    `reg` must include: jurisdiction, topic, title, citation, source_url,
    source_id, raw_text. summary/content_hash/applicability are derived if absent.
    """
    reg = dict(reg)
    reg.setdefault("summary", make_summary(reg.get("raw_text", "")))
    reg.setdefault("content_hash", content_hash(reg.get("raw_text", "")))
    reg.setdefault("status", "active")
    # applicability (multi-tenant filtering) — derived unless the caller supplies it
    reg.setdefault("domain", TOPIC_DOMAIN.get(reg.get("topic"), "safety"))
    reg.setdefault("employee_count_min", 1)  # safety standards apply to any employer
    reg.setdefault("industries", _industries_for(reg["citation"]))
    reg.setdefault("applies_when", _applies_when_for(reg["citation"]))
    reg["last_reviewed"] = _dt.date.today()

    with get_conn() as c, c.cursor() as cur:
        cur.execute(
            "select content_hash from compliance.regulations where citation = %s",
            (reg["citation"],),
        )
        row = cur.fetchone()
        outcome = "inserted" if row is None else (
            "unchanged" if row[0] == reg["content_hash"] else "changed"
        )
        cur.execute(
            "insert into compliance.regulations "
            "  (jurisdiction, topic, title, summary, citation, source_url, "
            "   status, raw_text, content_hash, source_id, last_reviewed, "
            "   domain, employee_count_min, applies_when, industries, updated_at) "
            "values (%(jurisdiction)s, %(topic)s, %(title)s, %(summary)s, %(citation)s, "
            "  %(source_url)s, %(status)s, %(raw_text)s, %(content_hash)s, %(source_id)s, "
            "  %(last_reviewed)s, %(domain)s, %(employee_count_min)s, %(applies_when)s, "
            "  %(industries)s, now()) "
            "on conflict (citation) do update set "
            "  jurisdiction = excluded.jurisdiction, topic = excluded.topic, "
            "  title = excluded.title, summary = excluded.summary, "
            "  source_url = excluded.source_url, status = excluded.status, "
            "  raw_text = excluded.raw_text, content_hash = excluded.content_hash, "
            "  source_id = excluded.source_id, last_reviewed = excluded.last_reviewed, "
            "  domain = excluded.domain, employee_count_min = excluded.employee_count_min, "
            "  applies_when = excluded.applies_when, industries = excluded.industries, "
            "  updated_at = now()",
            reg,
        )
        return outcome
