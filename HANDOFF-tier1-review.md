# Tier-1 Review page — hosting status (RESOLVED, no action needed)

**Updated:** 2026-06-12 · cdo-courtney-regs agent

## TL;DR for any other agent

**You don't need to do anything.** The Tier-1 review page is hosted from THIS
repo via GitHub Pages. The CDO repo is untouched.

- **Live URL:** https://mmamodelai.github.io/cdo-courtney-regs/
- **Source:** `index.html` in this repo (self-contained — data + Supabase
  writes inlined; review responses save to `compliance.section_reviews`)
- The copy briefly pushed to `mmamodelai/CDO` as `tier1-review.html`
  (commit 8525cb4) was **removed** (commit e952a50). The CDO repo and its
  Vercel deploy are back to exactly their prior state.

## How updates work

Normal git flow, this repo only:

```
python run_all.py                                  # rescrape + regenerate data
python -c "html=open('dashboard/Tier1-Review.html',encoding='utf-8').read(); data=open('dashboard/CDO-Project-Dashboard.data.js',encoding='utf-8').read(); open('index.html','w',encoding='utf-8').write(html.replace('<script src=\"CDO-Project-Dashboard.data.js\"></script>','<script>\n'+data+'\n</script>'))"
git add index.html && git commit -m "update review page" && git push
```

GitHub Pages rebuilds on push (~1 minute) and the live URL updates.

## Teardown when the review is done

Disable Pages (repo Settings → Pages, or
`gh api -X DELETE repos/mmamodelai/cdo-courtney-regs/pages`) and/or delete
`index.html`. The collected responses live in Supabase
(`compliance.section_reviews`) and survive the page's removal.

## Reading the results

- Latest verdict per (citation, reviewer): RPC `public.compliance_fetch_reviews()`
- Or: `SELECT * FROM compliance.section_reviews ORDER BY created_at DESC;`
- Sign-off rows: `citation = '__signoff__'`; suggestions: `citation LIKE '(suggested)%'`
