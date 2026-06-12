"""The change feed — what the watcher detected, awaiting human review.

Every scraper run that inserts a new regulation or sees its content_hash move
writes a row to compliance.regulatory_changes (status='detected'). Review flow:
detected → in_review → approved/rejected.

Run:  python show_changes.py               (all changes, newest first)
      python show_changes.py detected      (filter by status)
      python show_changes.py approve 12 eddie "looks right"
"""
import sys
import db as _db


def show(status=None):
    rows = _db._rpc("compliance_changes", {"p_status": status}) or []
    if not rows:
        print(f"No changes{f' with status={status}' if status else ''}.")
        return
    print(f"{len(rows)} change(s){f' [{status}]' if status else ''}:\n")
    for r in rows:
        old = (r["old_hash"] or "")[:10] or "—"
        print(f"  #{r['id']:<4} {r['detected_at'][:16]}  {r['change_type']:8} "
              f"{r['status']:10} {r['citation']}")
        print(f"        hash {old} -> {r['new_hash'][:10]}"
              + (f"  reviewed_by={r['reviewed_by']}" if r["reviewed_by"] else ""))


def review(change_id, status, who=None, notes=None):
    result = _db._rpc("compliance_review_change", {
        "p_id": int(change_id), "p_status": status,
        "p_reviewed_by": who, "p_notes": notes,
    })
    print(f"change #{change_id} → {status}: {result}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        show()
    elif args[0] in ("detected", "in_review", "approved", "rejected"):
        show(args[0])
    elif args[0] in ("approve", "reject", "start"):
        status = {"approve": "approved", "reject": "rejected", "start": "in_review"}[args[0]]
        review(args[1], status, args[2] if len(args) > 2 else None,
               args[3] if len(args) > 3 else None)
    else:
        print(__doc__)
