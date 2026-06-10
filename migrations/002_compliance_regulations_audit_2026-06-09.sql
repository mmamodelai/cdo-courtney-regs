-- ============================================================================
-- 002 — public.compliance_regulations audit corrections (2026-06-09)
-- ============================================================================
-- Source: "CDO Compliance Engine — Regulation Audit Brief" from Stephen Clare
--         (CDO Engineering) to Courtney Magee, 2026-06-09.
--
-- TARGET: public.compliance_regulations  (the PRODUCTION app catalog — 23 rows)
--         NOT compliance.regulations (the scraper sandbox). These are different
--         tables with different purposes.
--
-- ACCESS: the compliance_intern login has NO grants on this table. This MUST be
--         run by an admin / service role (Supabase SQL Editor) — the scraper
--         cannot apply it. This is the LIVE compliance engine for S&W: review
--         before running.
--
-- VERIFIED 2026-06-09 against primary sources + the live DB:
--   • id defaults to gen_random_uuid() → INSERTs below omit id intentionally.
--   • Target codes OSHA-1910.1200 and OSHA-1910.146 both exist (2 rows).
--   • New codes (silica / recordkeeping / prevailing wage) not already present.
--   • dir.ca.gov/title8/1731.html confirms: roof removal/tear-off covered;
--     >7:12 slope = fall protection regardless of height; 0:12–7:12 = 6 ft.
--   • dir.ca.gov/title8/sb4a37.html confirms: Title 8 Article 37, §§1950–1962,
--     "Confined Spaces in Construction".
--
-- NOTE (legal review still required before building FLAG/WAIVER logic on these):
--   • Silica §1926.1153 Table 1 task-matching for roofing tasks.
--   • A jobs.is_public_works flag is needed before the prevailing-wage check fires.
-- ============================================================================

begin;

-- ---- Part 1 · Citation fixes (2 records) -----------------------------------

-- Fix #1 — HazCom: 1910.1200 is general industry; construction needs 1926.59,
-- and CA §5194 is the controlling standard (adds Prop 65 Appendix G).
update public.compliance_regulations
set code        = 'OSHA-1926.59',
    description  = '29 CFR § 1926.59 (federal construction HazCom — incorporates 1910.1200 by '
                || 'reference) + Cal/OSHA Title 8 § 5194 (California controlling standard, adds '
                || 'Prop 65 Appendix G). Use § 5194 for CA enforcement citations.',
    source_url      = 'https://www.dir.ca.gov/title8/5194.html',
    last_updated_at = now()
where code = 'OSHA-1910.1200';

-- Fix #2 — Confined Space: 1910.146 is general industry. Construction has its
-- own rule; Cal/OSHA Article 37 was updated effective Jan 1, 2026.
update public.compliance_regulations
set code        = 'CAL-OSHA-1950',
    title        = 'Confined Space Entry (Construction)',
    description  = 'Cal/OSHA Title 8 Article 37 §§ 1950–1962 (construction-specific, effective '
                || 'Jan 1 2026) + Federal 29 CFR 1926 Subpart AA §§ 1926.1201–1213. Do NOT cite '
                || '§ 1910.146 — that is general industry only, a different standard.',
    source_url      = 'https://www.dir.ca.gov/title8/sb4a37.html',
    last_updated_at = now()
where code = 'OSHA-1910.146';

-- ---- Part 2 · Missing regulations (3 new records) --------------------------

-- Missing #1 — Respirable Crystalline Silica (highest-priority gap)
insert into public.compliance_regulations
  (code, title, description, source_url, applies_to, renewal_months,
   state, category, required_at_hire, conditional_note, active)
values
  ('CAL-OSHA-1532-3',
   'Respirable Crystalline Silica',
   'Cal/OSHA Title 8 § 1532.3 (construction) / Federal 29 CFR § 1926.1153. '
   || 'PEL 50 µg/m³, Action Level 25 µg/m³ (8-hr TWA). NOT just training — triggers a full '
   || 'written compliance program: exposure control plan, air monitoring, respiratory '
   || 'protection, medical surveillance (workers above PEL ≥ 30 days/yr), HazCom, '
   || 'recordkeeping. Tile cutting: 70–380 µg/m³; concrete grinding: up to 1,730 µg/m³. '
   || '§ 1926.1153 Table 1 lists 18 task categories — match roofing tasks to Table 1 or '
   || 'conduct air monitoring under paragraph (d).',
   'https://www.dir.ca.gov/title8/1532_3.html',
   array['roofer','laborer'], 12, 'CA', 'safety', false,
   'Required when any employee may be occupationally exposed at or above the action level '
   || '(25 µg/m³). Virtually all grinding/cutting tasks on roofing sites qualify.',
   true);

-- Missing #2 — Injury & Illness Recordkeeping (OSHA 300/300A/301)
insert into public.compliance_regulations
  (code, title, description, source_url, applies_to, renewal_months,
   state, category, required_at_hire, conditional_note, active)
values
  ('CAL-OSHA-342',
   'Injury & Illness Recordkeeping (OSHA 300/300A/301)',
   'Cal/OSHA § 342 (serious-injury reporting) + § 14300 series (recordkeeping). Federal '
   || '29 CFR Part 1904. At 65 employees S&W must maintain Forms 300/300A/301, post 300A '
   || 'Feb 1–Apr 30 annually, AND submit 300A electronically under 29 CFR § 1904.41. Roofing '
   || '(NAICS 23816) is NOT on the partial-exemption list. Report to Cal/OSHA within 8 hrs '
   || '(fatality/hospitalization) or 24 hrs (amputation/eye loss) per § 342.',
   'https://www.dir.ca.gov/title8/14300.html',
   array['company'], 12, 'CA', 'compliance', false,
   'Applies to all employers with 11+ employees. Electronic 300A submission required; '
   || 'roofing is a high-hazard industry, not partially exempt.',
   true);

-- Missing #3 — Prevailing Wage / Public Works (S&W does public works)
insert into public.compliance_regulations
  (code, title, description, source_url, applies_to, renewal_months,
   state, category, required_at_hire, conditional_note, active)
values
  ('CA-LC-1771',
   'Prevailing Wage — Public Works',
   'California Labor Code §§ 1771 / 1775 / 1776 / 1777.5. Applies to all public works '
   || 'contracts. (1) DIR registration $400/yr BEFORE work begins; (2) pay prevailing wage '
   || 'per DIR determinations (updated 2×/yr); (3) monthly eCPR certified payroll via '
   || 'efiling.dir.ca.gov/eCPR/; (4) apprenticeship ratio 1:5 on projects ≥ $30K (§ 1777.5). '
   || 'Penalty: $200/day per underpaid worker (§ 1775). Craft codes: Roofer + Metal Roofing '
   || 'System Installer. Rates vary by county — dir.ca.gov/oprl/dprewagedetermination.htm.',
   'https://www.dir.ca.gov/public-works/prevailing-wage.html',
   array['company'], 12, 'CA', 'compliance', false,
   'Applies ONLY to public works projects. DIR registration mandatory before any public '
   || 'works job begins. Needs a jobs.is_public_works flag before the engine can fire this.',
   true);

-- ---- Part 3 · Fall-protection enrichment (keep federal cites, ADD CA) ------
-- The brief: records #18/#19 cite correct federal standards but are incomplete —
-- Cal/OSHA §§ 1730/1731 are the controlling CA authority. Append, do not replace.

update public.compliance_regulations
set description = description
      || ' | CA controlling authority: Cal/OSHA Title 8 § 1731 (residential-type, incl. roof '
      || 'removal/tear-off — fall protection regardless of height for slopes > 7:12; 6 ft for '
      || '0:12–7:12) and § 1730 (other roofing). Amended effective July 1 2025.',
    last_updated_at = now()
where code in ('OSHA-1926.502-CP','OSHA-1926.503');

-- ---- Optional · data-quality fix found during reconciliation (not in brief) -
-- § 1730 is "Roof Hazards", not "Hot Tar/Asphalt Roofing Safety" (confirmed via
-- dir.ca.gov/title8/1730.html). Uncomment to correct the title.
-- update public.compliance_regulations
-- set title = 'Roof Hazards (slope, edges, openings)', last_updated_at = now()
-- where code = 'CAL-OSHA-1730';

commit;

-- Sanity check after running:
-- select code, title, category from public.compliance_regulations order by category, code;
-- Expect 26 rows (23 − 0 deleted + 3 inserted; 2 codes renamed).
