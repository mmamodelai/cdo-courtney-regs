-- ============================================================================
-- 004 — section_reviews: human sign-off layer (2026-06-10)  [APPLIED 2026-06-10]
-- ============================================================================
-- Backs dashboard/Tier1-Review.html — the page Eddie & Melissa use to verify
-- the Tier-1 regulation list (charter: facts must be human-confirmed before
-- go-live). Append-only; the latest row per (citation, reviewer) is the
-- current verdict.
--   verdict: confirm  — section is correct & belongs in the list
--            flag     — something wrong (note required in UI)
--            suggest  — a missing section/regulation they propose adding
--            signoff  — reviewer signs off the whole list (citation='__signoff__')
-- ============================================================================

begin;

CREATE TABLE IF NOT EXISTS compliance.section_reviews (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  citation    text NOT NULL,
  reviewer    text NOT NULL,
  verdict     text NOT NULL CHECK (verdict IN ('confirm','flag','suggest','signoff')),
  note        text,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS section_reviews_cit_idx ON compliance.section_reviews (citation, reviewer, created_at DESC);

CREATE OR REPLACE FUNCTION public.compliance_submit_review(
  p_citation text, p_reviewer text, p_verdict text, p_note text DEFAULT NULL)
RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path = compliance, public
AS $$
DECLARE v_id bigint;
BEGIN
  IF length(trim(p_reviewer)) < 2 THEN RAISE EXCEPTION 'reviewer required'; END IF;
  INSERT INTO compliance.section_reviews (citation, reviewer, verdict, note)
  VALUES (p_citation, trim(p_reviewer), p_verdict, nullif(trim(coalesce(p_note,'')), ''))
  RETURNING id INTO v_id;
  RETURN v_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.compliance_fetch_reviews()
RETURNS TABLE (citation text, reviewer text, verdict text, note text, created_at timestamptz)
LANGUAGE sql SECURITY DEFINER SET search_path = compliance, public
AS $$
  SELECT DISTINCT ON (citation, reviewer)
         citation, reviewer, verdict, note, created_at
  FROM compliance.section_reviews
  ORDER BY citation, reviewer, created_at DESC;
$$;

GRANT EXECUTE ON FUNCTION public.compliance_submit_review(text, text, text, text) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.compliance_fetch_reviews() TO anon, authenticated, service_role;

commit;
