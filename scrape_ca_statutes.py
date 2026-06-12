"""Scrape California statutes (leginfo) into compliance.regulations.

Covers the employer-compliance DOMAINS that live in CA statutes (not Title 8):
wage & hour, leave & benefits, harassment / EEO / violence, licensing / insurance,
and prevailing wage. Spans multiple codes — Labor (LAB), Government (GOV), and
Business & Professions (BPC) — all served by the same leginfo section view.

Every row is tagged with its domain + applicability (employee_count_min,
industries, applies_when) so the onboarding engine can filter per client. This is
where headcount triggers get real: CFRA / harassment training kick in at 5+
employees, school-activities leave at 25+, prevailing wage only on public works.

leginfo is a slow JSF app, so we use a session + retries + a generous timeout, and
slice from the section marker to drop the leading code/branch breadcrumb.

Run:  python scrape_ca_statutes.py
"""
import re
import time
import warnings

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from osha_common import (
    HEADERS, normalize_text, upsert_source, upsert_regulation, setup_schema,
)

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

SECTION_URL = ("https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml"
               "?lawCode={code}&sectionNum={sec}.")

CODE_LABEL = {
    "LAB": "Cal. Lab. Code",
    "GOV": "Cal. Gov. Code",
    "BPC": "Cal. Bus. & Prof. Code",
    "UIC": "Cal. Unemp. Ins. Code",
    "CIV": "Cal. Civ. Code",
    "VEH": "Cal. Veh. Code",
    "MVC": "Cal. Mil. & Vet. Code",
}

STATUTE_SOURCE = {
    "name": "California statutes — leginfo (Labor / Government / B&P Codes)",
    "url": "https://leginfo.legislature.ca.gov/faces/codesTOCSelected.xhtml?tocCode=LAB",
    "kind": "scrape",
    "jurisdiction": "CA",
    "notes": "Authoritative CA statute text from the Legislature, across codes. "
             "Backs the non-safety compliance domains (wage/hour, leave, harassment, "
             "licensing, prevailing wage).",
}

# (code, section, domain, topic, name, applies_when, employee_count_min)
CA_STATUTES = [
    # ---- WAGE & HOUR (Labor Code) ----
    ("LAB", "510",     "wage_hour", "overtime",        "Overtime — daily/weekly rates (1.5× after 8h/day & 40h/week, 2× after 12h)", "non-exempt employees", 1),
    ("LAB", "512",     "wage_hour", "meal_rest",       "Meal periods — 30-min meal by the 5th hour; second meal by the 10th",        "non-exempt employees; shifts over 5 hours", 1),
    ("LAB", "226",     "wage_hour", "wage_statements", "Itemized wage statements — required pay-stub line items",                    None, 1),
    ("LAB", "201",     "wage_hour", "final_pay",       "Final pay on discharge — wages due immediately",                            None, 1),
    ("LAB", "202",     "wage_hour", "final_pay",       "Final pay on resignation — within 72 hours (immediately if 72h notice)",    None, 1),
    ("LAB", "203",     "wage_hour", "final_pay",       "Waiting-time penalty — up to 30 days' wages for late final pay",            None, 1),
    ("LAB", "1182.12", "wage_hour", "minimum_wage",    "State minimum wage",                                                        None, 1),
    ("LAB", "2810.5",  "wage_hour", "wage_notice",     "Wage Theft Prevention Act — written pay notice to employees at hire",       None, 1),
    # ---- LEAVE & BENEFITS ----
    ("LAB", "246",     "leave_benefits", "paid_sick_leave",     "Paid sick leave — accrual, use & rate (HWHFA)",                None, 1),
    ("LAB", "233",     "leave_benefits", "paid_sick_leave",     "Kin care — use of accrued sick leave for family",              None, 1),
    ("GOV", "12945.2", "leave_benefits", "family_medical_leave","California Family Rights Act (CFRA) — job-protected leave",     "employers with 5+ employees", 5),
    ("GOV", "12945",   "leave_benefits", "family_medical_leave","Pregnancy Disability Leave (PDL)",                             "employers with 5+ employees", 5),
    ("GOV", "12945.7", "leave_benefits", "bereavement_leave",   "Bereavement leave (AB 1949)",                                  "employers with 5+ employees", 5),
    ("LAB", "230",     "leave_benefits", "civic_leave",         "Jury, witness & victim leave; protected time off",             None, 1),
    ("LAB", "230.8",   "leave_benefits", "civic_leave",         "Time off for a child's school activities",                     "employers with 25+ employees", 25),
    # ---- HARASSMENT / EEO / VIOLENCE ----
    ("GOV", "12940",   "harassment_eeo", "discrimination",      "FEHA — unlawful employment practices (discrimination & harassment)", "employers with 5+ (harassment: any size)", 5),
    ("GOV", "12950.1", "harassment_eeo", "harassment_training", "Sexual harassment prevention training (SB 1343)",              "employers with 5+ employees", 5),
    ("LAB", "6401.9",  "harassment_eeo", "workplace_violence",  "Workplace Violence Prevention Plan (SB 553)",                  None, 1),
    # ---- LICENSING / INSURANCE ----
    ("LAB", "3700",    "licensing_insurance", "workers_comp",      "Workers' compensation insurance — required coverage",       None, 1),
    ("BPC", "7065",    "licensing_insurance", "contractor_license","Contractors' license — examination & issuance (CSLB)",      None, 1),
    # ---- PREVAILING WAGE (public works) ----
    ("LAB", "1771",    "prevailing_wage", "prevailing_wage", "Prevailing wages required on public works",          "public works projects", 1),
    ("LAB", "1775",    "prevailing_wage", "prevailing_wage", "Prevailing wage — penalties for underpayment",       "public works projects", 1),
    ("LAB", "1777.5",  "prevailing_wage", "prevailing_wage", "Apprenticeship requirements on public works",        "public works projects ≥ $30k", 1),
    # ---- WAGE & HOUR (additional employer obligations) ----
    ("LAB", "2802",    "wage_hour", "expense_reimbursement", "Reimbursement of necessary business expenses",        None, 1),
    ("LAB", "551",     "wage_hour", "day_of_rest",           "Day of rest — one day's rest in seven",               None, 1),
    ("LAB", "552",     "wage_hour", "day_of_rest",           "Day of rest — employer may not cause work more than 6 days in 7", None, 1),
    ("LAB", "432.3",   "wage_hour", "pay_transparency",      "Pay scale disclosure / pay transparency",             "pay scale in job postings: 15+ employees", 15),
    ("LAB", "1198.5",  "wage_hour", "personnel_records",     "Employee right to inspect personnel records",         None, 1),
    # ---- LEAVE & BENEFITS (additional) ----
    ("LAB", "1030",    "leave_benefits", "lactation",      "Lactation accommodation — break time",                    None, 1),
    ("LAB", "1031",    "leave_benefits", "lactation",      "Lactation accommodation — location requirements",         None, 1),
    ("LAB", "1034",    "leave_benefits", "lactation",      "Lactation room/space requirements (SB 142)",              None, 1),
    ("MVC", "394",     "leave_benefits", "military_leave", "Military leave & protection from discrimination (CA)",   "employees in military service", 1),
    # ---- HARASSMENT / EEO (additional) ----
    ("GOV", "12952",   "harassment_eeo", "fair_chance",   "Fair Chance Act — criminal history (ban-the-box)",       "employers with 5+ employees", 5),
    ("LAB", "1102.5",  "harassment_eeo", "whistleblower", "Whistleblower protection / anti-retaliation",            None, 1),
    # ---- WORKER CLASSIFICATION ----
    ("LAB", "2775",    "worker_classification", "ab5",     "Independent-contractor ABC test (AB 5 / AB 2257)",       "engaging independent contractors", 1),
    # ---- RETIREMENT / BENEFITS ----
    ("GOV", "100032",  "benefits_retirement", "calsavers", "CalSavers — state retirement savings mandate",          "no qualified employer retirement plan offered", 1),
    # ---- PRIVACY & CONDUCT ----
    ("LAB", "980",     "privacy_conduct", "social_media",       "Social media privacy — no access to personal accounts", None, 1),
    ("CIV", "3426.1",  "privacy_conduct", "trade_secrets",      "Trade secrets — Uniform Trade Secrets Act (definitions)", None, 1),
    ("VEH", "23123.5", "privacy_conduct", "distracted_driving", "Handheld phone / texting while driving prohibited",     "employees who drive for work", 1),
    # ---- WORKFORCE REDUCTION ----
    ("LAB", "1400",    "workforce_reduction", "warn_act", "Cal/WARN Act — short title",                              "75+ employees", 75),
    ("LAB", "1400.5",  "workforce_reduction", "warn_act", "Cal/WARN — definitions (covered establishment, mass layoff)", "75+ employees", 75),
    ("LAB", "1401",    "workforce_reduction", "warn_act", "Cal/WARN — 60-day written notice before mass layoff/closure", "75+ employees", 75),
    ("LAB", "1402",    "workforce_reduction", "warn_act", "Cal/WARN — employer liability for failure to give notice",    "75+ employees", 75),
]


def fetch_section(session, code, section, tries=3):
    """Return clean statute text for a section, or None. leginfo is flaky."""
    url = SECTION_URL.format(code=code, sec=section)
    last = None
    for attempt in range(tries):
        try:
            r = session.get(url, timeout=90)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
            body = soup.find(id="codeLawSectionNoHead")
            if body is None:
                last = "no codeLawSectionNoHead container"
                continue
            text = normalize_text(body.get_text("\n"))
            # Drop the leading "<Name> Code - XXX DIVISION ..." breadcrumb: slice
            # from the section number marker (not preceded by a digit/dot).
            m = re.search(rf"(?<![\d.]){re.escape(section)}\.\s", text)
            if m:
                text = text[m.start():]
            if len(text) < 30:
                last = f"text too short ({len(text)})"
                continue
            return text
        except Exception as e:
            last = str(e)
            time.sleep(2 * (attempt + 1))
    print(f"    ! {code} {section}: {last}")
    return None


def main():
    setup_schema()
    print("California statutes — leginfo (wage/hour · leave · harassment · licensing · prevailing wage)")
    source_id = upsert_source(STATUTE_SOURCE)
    session = requests.Session()
    session.headers.update(HEADERS)

    tally = {"inserted": 0, "changed": 0, "unchanged": 0, "missing": 0}
    by_domain = {}
    for code, section, domain, topic, name, applies_when, min_emp in CA_STATUTES:
        text = fetch_section(session, code, section)
        if text is None:
            tally["missing"] += 1
            continue
        label = CODE_LABEL[code]
        outcome = upsert_regulation({
            "jurisdiction": "CA",
            "topic": topic,
            "title": f"{label} § {section} — {name}",
            "citation": f"{label} § {section}",
            "source_url": SECTION_URL.format(code=code, sec=section),
            "source_id": source_id,
            "raw_text": text,
            "domain": domain,
            "employee_count_min": min_emp,
            "industries": ["all"],
            "applies_when": applies_when,
        })
        tally[outcome] += 1
        by_domain[domain] = by_domain.get(domain, 0) + 1
        print(f"  {outcome:9} {label} § {section:8} [{domain}] {name[:48]}")
        time.sleep(1)  # be polite to leginfo

    print(f"\nCA statutes done: {tally}")
    print("  by domain:", by_domain)


if __name__ == "__main__":
    main()
