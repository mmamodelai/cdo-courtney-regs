"""Generate the dashboard's DATA from the live database — no hardcoded data points.

Writes ../CDO-Project-Dashboard.data.js (window.CDO_DATA = {...}) which the HTML
loads. Every regulation row, count, topic, and Critical-30 coverage status is
computed from compliance.regulations at build time. Re-run after any scrape:

    python run_all.py && python build_dashboard.py

The HTML is the VIEW; this is the DATA. The only authored bits here are the topic
display registry (names/colors) and the Critical-30 target map — curation, not
scraped facts — and even their coverage status is computed against the DB.
"""
import json
import datetime as _dt

import db as _db
from explainers import EXPLAINERS, coverage_check

OUT = "dashboard/CDO-Project-Dashboard.data.js"

# Topic display registry (name + color). Curation only — pure presentation.
TOPIC = {
    "fall_protection":   {"n": "Fall Protection",      "c": "#ff6b6b"},
    "roofing_ops":       {"n": "Roofing Ops",          "c": "#f5b301"},
    "heat_illness":      {"n": "Heat Illness",         "c": "#f97316"},
    "respiratory_hazmat":{"n": "Respiratory / Hazmat", "c": "#a855f7"},
    "ppe":               {"n": "PPE",                  "c": "#22d3ee"},
    "materials_handling":{"n": "Materials / Debris",   "c": "#34d399"},
    "ladders":           {"n": "Ladders",              "c": "#60a5fa"},
    "scaffolds":         {"n": "Scaffolds",            "c": "#818cf8"},
    "hazcom":            {"n": "HazCom",               "c": "#fbbf24"},
    "safety_program":    {"n": "IIPP / Safety Program","c": "#14b8a6"},
    "lockout_tagout":    {"n": "Lockout/Tagout",       "c": "#f472b6"},
    "fire_safety":       {"n": "Fire Safety",          "c": "#fb7185"},
    "first_aid":         {"n": "First Aid",            "c": "#4ade80"},
    "confined_space":    {"n": "Confined Space",       "c": "#94a3b8"},
    # wage & hour domain
    "overtime":          {"n": "Overtime",             "c": "#2dd4bf"},
    "meal_rest":         {"n": "Meal & Rest",          "c": "#5eead4"},
    "wage_statements":   {"n": "Wage Statements",      "c": "#38bdf8"},
    "final_pay":         {"n": "Final Pay",            "c": "#a78bfa"},
    "minimum_wage":      {"n": "Minimum Wage",         "c": "#84cc16"},
    "wage_notice":       {"n": "Wage Theft Notice",    "c": "#f0abfc"},
    # leave & benefits
    "paid_sick_leave":     {"n": "Paid Sick Leave",      "c": "#fcd34d"},
    "family_medical_leave":{"n": "Family/Medical Leave", "c": "#fca5a5"},
    "bereavement_leave":   {"n": "Bereavement",          "c": "#d8b4fe"},
    "civic_leave":         {"n": "Jury/Civic Leave",     "c": "#93c5fd"},
    # harassment / EEO / violence
    "discrimination":      {"n": "FEHA / Discrimination","c": "#f9a8d4"},
    "harassment_training": {"n": "Harassment Training",  "c": "#fdba74"},
    "workplace_violence":  {"n": "Workplace Violence",   "c": "#e879f9"},
    # licensing / insurance / prevailing wage
    "workers_comp":        {"n": "Workers' Comp",        "c": "#67e8f9"},
    "contractor_license":  {"n": "Contractor License",   "c": "#facc15"},
    "prevailing_wage":     {"n": "Prevailing Wage",      "c": "#bef264"},
    # federal employment law (29 CFR)
    "fmla":          {"n": "FMLA (federal)",  "c": "#f87171"},
    "flsa_overtime": {"n": "FLSA Overtime",   "c": "#06b6d4"},
    "flsa_exempt":   {"n": "FLSA Exemptions", "c": "#0ea5e9"},
    "ada":           {"n": "ADA (federal)",   "c": "#c084fc"},
    "title_vii":     {"n": "Title VII",       "c": "#ec4899"},
    # additional employer obligations
    "expense_reimbursement": {"n": "Expense Reimbursement", "c": "#34d399"},
    "day_of_rest":           {"n": "Day of Rest",           "c": "#a3e635"},
    "pay_transparency":      {"n": "Pay Transparency",      "c": "#fde047"},
    "personnel_records":     {"n": "Personnel Records",     "c": "#7dd3fc"},
    "lactation":             {"n": "Lactation",             "c": "#fbcfe8"},
    "military_leave":        {"n": "Military Leave",        "c": "#86efac"},
    "fair_chance":           {"n": "Fair Chance / Ban-Box", "c": "#fca5a5"},
    "whistleblower":         {"n": "Whistleblower",         "c": "#fde68a"},
    "ab5":                   {"n": "Worker Classification", "c": "#c4b5fd"},
    "calsavers":             {"n": "CalSavers Retirement",  "c": "#6ee7b7"},
    "social_media":          {"n": "Social Media Privacy",  "c": "#93c5fd"},
    "trade_secrets":         {"n": "Trade Secrets",         "c": "#d4d4d8"},
    "distracted_driving":    {"n": "Distracted Driving",    "c": "#fdba74"},
    "warn_act":              {"n": "WARN Act (layoffs)",    "c": "#f9a8d4"},
    # EDD programs + IWC wage orders
    "pfl":        {"n": "Paid Family Leave (PFL)",  "c": "#fda4af"},
    "sdi":        {"n": "Disability Ins. (SDI)",    "c": "#a5b4fc"},
    "wage_order": {"n": "Wage Order 16 (constr.)",  "c": "#fbbf24"},
}

# Critical-30 SAFETY (Master Plan §12): policy -> the citation that satisfies it.
# Coverage is COMPUTED below by checking which of these exist in the DB.
CRIT30_TARGETS = [
    ("01", "IIPP — Injury & Illness Prevention Program", "8 CCR § 3203"),
    ("02", "Heat Illness Prevention",                    "8 CCR § 3395"),
    ("03", "Fall Protection in Construction",            "8 CCR § 1670"),
    ("04", "Respiratory Protection",                     "8 CCR § 5144"),
    ("05", "Confined Space Entry (construction)",        "8 CCR § 1950"),
    ("06", "Hazard Communication / HazCom",              "8 CCR § 5194"),
    ("07", "PPE — Personal Protective Equipment",        "8 CCR § 3380"),
    ("08", "Lockout / Tagout",                           "8 CCR § 3314"),
    ("09", "Fire Safety",                                "8 CCR § 3221"),
    ("10", "First Aid + CPR readiness",                  "8 CCR § 3400"),
]


def fetch():
    regs = []
    present = set()
    for row in (_db._rpc("compliance_fetch_regulations", {}) or []):
        title = row["title"]
        name = title.split(" — ", 1)[1] if " — " in title else title
        regs.append({"jur": row["jurisdiction"], "cit": row["citation"],
                     "title": name, "topic": row["topic"],
                     "chars": row["chars"] or 0, "url": row["source_url"],
                     "hash": row["hash"],
                     "domain": row["domain"], "minEmp": row["employee_count_min"],
                     "appliesWhen": row["applies_when"],
                     "industries": row["industries"] or [],
                     "explainer": EXPLAINERS.get(row["citation"], "")})
        present.add(row["citation"])
    sources = [{"jur": r["jurisdiction"], "name": r["name"], "kind": r["kind"],
                "url": r["url"], "scraped": r["scraped"],
                "note": r["notes"], "n": r["reg_count"]}
               for r in (_db._rpc("compliance_fetch_sources", {}) or [])]
    return regs, sources, present


def build_crit30(present):
    rows = []
    for n, policy, cit in CRIT30_TARGETS:
        ok = cit in present
        rows.append({"n": n, "p": policy, "cit": cit,
                     "st": "ok" if ok else "miss",
                     "our": (cit + " ✓") if ok else "— (not yet in DB)"})
    return rows


def main():
    regs, sources, present = fetch()
    crit30 = build_crit30(present)
    tables = _db._rpc("compliance_table_counts", {}) or {}
    missing = coverage_check(present)
    if missing:
        print(f"  !! {len(missing)} regulation(s) have NO explainer (write them in "
              f"explainers.py): {', '.join(missing)}")
    # build timestamp is injected (Date.now is fine in plain Python here)
    data = {
        "regs": regs,
        "sources": sources,
        "topic": TOPIC,
        "crit30": crit30,
        "tables": tables,
        "generatedAt": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "counts": {
            "total": len(regs),
            "ca": sum(1 for r in regs if r["jur"] == "CA"),
            "federal": sum(1 for r in regs if r["jur"] == "Federal"),
            "topics": len({r["topic"] for r in regs}),
            "chars": sum(r["chars"] for r in regs),
            "crit30_ok": sum(1 for r in crit30 if r["st"] == "ok"),
            "crit30_total": len(crit30),
        },
        "domains": sorted({r["domain"] for r in regs if r["domain"]}),
    }
    js = "// AUTO-GENERATED by build_dashboard.py — do not edit by hand.\n" \
         "window.CDO_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(js)
    cc = data["counts"]
    print(f"Wrote {OUT}")
    print(f"  {cc['total']} regs ({cc['federal']} federal, {cc['ca']} CA) · "
          f"{cc['topics']} topics · {cc['chars']:,} chars · "
          f"Critical-30 safety {cc['crit30_ok']}/{cc['crit30_total']}")


if __name__ == "__main__":
    main()
