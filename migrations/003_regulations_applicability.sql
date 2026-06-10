-- 003 — applicability as first-class data (multi-tenant filtering).
-- Run by an admin (compliance_intern lacks DDL). Applied 2026-06-09.
alter table compliance.regulations
  add column if not exists domain             text,
  add column if not exists employee_count_min integer,
  add column if not exists applies_when        text,
  add column if not exists industries          text[];
