-- 001_watcher_keys.sql
-- Run ONCE by a role that owns the compliance tables (e.g. postgres / an admin).
-- The compliance_intern login has DML only (insert/update/select) and cannot run
-- this DDL, so an admin (Stephen) applies it. Additive and idempotency-safe.
--
-- Adds:
--   * unique key on sources.url        -> idempotent source upserts
--   * unique key on regulations.citation -> idempotent regulation upserts
--   * regulations.content_hash         -> change-detection signal for the watcher

alter table compliance.sources
  add constraint sources_url_key unique (url);

alter table compliance.regulations
  add constraint regulations_citation_key unique (citation);

alter table compliance.regulations
  add column if not exists content_hash text;
