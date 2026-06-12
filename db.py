"""DB helper for the compliance scraper.

Connects to Supabase via REST API using SECURITY DEFINER RPCs in the public
schema. No direct Postgres connection needed — the anon key is sufficient
because the RPCs run as the function owner and have full compliance schema access.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

_URL = os.environ["SUPABASE_URL"].rstrip("/")
_KEY = os.environ["SUPABASE_ANON_KEY"]
_HEADERS = {
    "apikey": _KEY,
    "Authorization": f"Bearer {_KEY}",
    "Content-Type": "application/json",
}


def _rpc(fn: str, params: dict):
    """Call a Supabase RPC function and return the parsed JSON response."""
    r = requests.post(f"{_URL}/rest/v1/rpc/{fn}", json=params, headers=_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def list_tables():
    return _rpc("compliance_list_tables", {}) or []


def check_setup():
    return _rpc("compliance_setup_check", {})


def upsert_source(source: dict) -> int:
    return _rpc("compliance_upsert_source", {
        "p_name": source["name"],
        "p_url": source["url"],
        "p_kind": source["kind"],
        "p_jurisdiction": source["jurisdiction"],
        "p_notes": source.get("notes"),
    })


def upsert_regulation(reg: dict) -> str:
    import datetime as _dt
    last_reviewed = reg.get("last_reviewed", _dt.date.today())
    if isinstance(last_reviewed, _dt.date):
        last_reviewed = last_reviewed.isoformat()
    return _rpc("compliance_upsert_regulation", {
        "p_jurisdiction": reg["jurisdiction"],
        "p_topic": reg["topic"],
        "p_title": reg["title"],
        "p_summary": reg.get("summary", ""),
        "p_citation": reg["citation"],
        "p_source_url": reg["source_url"],
        "p_status": reg.get("status", "active"),
        "p_raw_text": reg.get("raw_text", ""),
        "p_content_hash": reg.get("content_hash", ""),
        "p_source_id": reg["source_id"],
        "p_last_reviewed": last_reviewed,
        "p_domain": reg.get("domain", "safety"),
        "p_employee_count_min": reg.get("employee_count_min", 1),
        "p_applies_when": reg.get("applies_when"),
        "p_industries": reg.get("industries", ["all"]),
    })


if __name__ == "__main__":
    print("compliance tables:", list_tables())
    print("migration check:", check_setup())
