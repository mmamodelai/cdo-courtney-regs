-- ============================================================================
-- 003 — change-detection watcher (2026-06-10)  [APPLIED 2026-06-10 via admin MCP]
-- ============================================================================
-- Creates compliance.regulatory_changes (Master Plan "regulatory_changes",
-- scoped to the compliance sandbox) and upgrades compliance_upsert_regulation
-- so every 'inserted' / 'changed' outcome writes a change row automatically.
-- Layer A→B of the Compliance Brain: the scraper now EMITS a change feed.
--
-- Review workflow:  detected → in_review → approved | rejected
--   read:    select * from public.compliance_changes(null | 'detected' | ...)
--   review:  select public.compliance_review_change(id, 'approved', 'eddie', 'note')
--   CLI:     python show_changes.py [status]
-- ============================================================================

begin;

CREATE TABLE IF NOT EXISTS compliance.regulatory_changes (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  citation     text NOT NULL,
  change_type  text NOT NULL CHECK (change_type IN ('new','modified')),
  old_hash     text,
  new_hash     text NOT NULL,
  summary      text,
  detected_at  timestamptz NOT NULL DEFAULT now(),
  status       text NOT NULL DEFAULT 'detected'
               CHECK (status IN ('detected','in_review','approved','rejected')),
  reviewed_at  timestamptz,
  reviewed_by  text,
  notes        text
);
CREATE INDEX IF NOT EXISTS regulatory_changes_status_idx
  ON compliance.regulatory_changes (status, detected_at DESC);

CREATE OR REPLACE FUNCTION public.compliance_upsert_regulation(
  p_jurisdiction text, p_topic text, p_title text, p_summary text,
  p_citation text, p_source_url text, p_status text, p_raw_text text,
  p_content_hash text, p_source_id bigint, p_last_reviewed date,
  p_domain text, p_employee_count_min integer, p_applies_when text,
  p_industries text[])
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'compliance', 'public'
AS $function$
DECLARE v_existing text;
BEGIN
  SELECT content_hash INTO v_existing FROM compliance.regulations WHERE citation = p_citation;
  INSERT INTO compliance.regulations (
    jurisdiction, topic, title, summary, citation, source_url,
    status, raw_text, content_hash, source_id, last_reviewed,
    domain, employee_count_min, applies_when, industries, updated_at
  ) VALUES (
    p_jurisdiction, p_topic, p_title, p_summary, p_citation, p_source_url,
    p_status, p_raw_text, p_content_hash, p_source_id, p_last_reviewed,
    p_domain, p_employee_count_min, p_applies_when, p_industries, now()
  )
  ON CONFLICT (citation) DO UPDATE SET
    jurisdiction = EXCLUDED.jurisdiction, topic = EXCLUDED.topic,
    title = EXCLUDED.title, summary = EXCLUDED.summary,
    source_url = EXCLUDED.source_url, status = EXCLUDED.status,
    raw_text = EXCLUDED.raw_text, content_hash = EXCLUDED.content_hash,
    source_id = EXCLUDED.source_id, last_reviewed = EXCLUDED.last_reviewed,
    domain = EXCLUDED.domain, employee_count_min = EXCLUDED.employee_count_min,
    applies_when = EXCLUDED.applies_when, industries = EXCLUDED.industries,
    updated_at = now();

  IF v_existing IS NULL THEN
    INSERT INTO compliance.regulatory_changes (citation, change_type, old_hash, new_hash, summary)
    VALUES (p_citation, 'new', NULL, p_content_hash, p_summary);
    RETURN 'inserted';
  ELSIF v_existing = p_content_hash THEN
    RETURN 'unchanged';
  ELSE
    INSERT INTO compliance.regulatory_changes (citation, change_type, old_hash, new_hash, summary)
    VALUES (p_citation, 'modified', v_existing, p_content_hash, p_summary);
    RETURN 'changed';
  END IF;
END;
$function$;

CREATE OR REPLACE FUNCTION public.compliance_changes(p_status text DEFAULT NULL)
RETURNS TABLE (id bigint, citation text, change_type text, old_hash text,
               new_hash text, summary text, detected_at timestamptz,
               status text, reviewed_by text, notes text)
LANGUAGE sql SECURITY DEFINER SET search_path = compliance, public
AS $$
  SELECT id, citation, change_type, old_hash, new_hash, summary,
         detected_at, status, reviewed_by, notes
  FROM compliance.regulatory_changes
  WHERE p_status IS NULL OR status = p_status
  ORDER BY detected_at DESC;
$$;

CREATE OR REPLACE FUNCTION public.compliance_review_change(
  p_id bigint, p_status text, p_reviewed_by text DEFAULT NULL, p_notes text DEFAULT NULL)
RETURNS text
LANGUAGE plpgsql SECURITY DEFINER SET search_path = compliance, public
AS $$
BEGIN
  UPDATE compliance.regulatory_changes
  SET status = p_status, reviewed_at = now(),
      reviewed_by = COALESCE(p_reviewed_by, reviewed_by),
      notes = COALESCE(p_notes, notes)
  WHERE id = p_id;
  IF NOT FOUND THEN RETURN 'not_found'; END IF;
  RETURN 'ok';
END;
$$;

GRANT EXECUTE ON FUNCTION public.compliance_changes(text) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.compliance_review_change(bigint, text, text, text) TO anon, authenticated, service_role;

commit;
