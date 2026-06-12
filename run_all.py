"""Run every roof tear-off scraper and print a combined summary.

This is the entry point you'd put on a schedule (cron / Task Scheduler) once the
data is trusted. Re-running is safe: rows are upserted by citation, so you only
ever get inserts for new sections and updates for changed text.

Run:  python run_all.py
"""
import register_sources
import scrape_osha_federal
import scrape_fed_employment
import scrape_calosha_title8
import scrape_ca_statutes
import scrape_ca_edd
import scrape_iwc_wage_order
import build_dashboard
import db_export


def main():
    print("=" * 70)
    register_sources.main()            # the full source watch-list (M2 inventory)
    print("=" * 70)
    scrape_osha_federal.main()         # 29 CFR 1926 + incorporated 1910 standards
    print("=" * 70)
    scrape_fed_employment.main()       # 29 CFR FMLA/FLSA/ADA/Title VII + 20 CFR USERRA
    print("=" * 70)
    scrape_calosha_title8.main()       # CA Title 8 — safety
    print("=" * 70)
    scrape_ca_statutes.main()          # CA Labor/Gov/B&P — wage, leave, harassment, licensing
    print("=" * 70)
    scrape_ca_edd.main()               # EDD — PFL & SDI (UIC not servable via leginfo)
    print("=" * 70)
    scrape_iwc_wage_order.main()       # IWC Wage Order 16 — on-site construction (PDF)
    print("=" * 70)
    # Regenerate the dashboard data + DB exports from the live DB so they're never
    # stale, hand-maintained snapshots (operating principle: no hardcoded data).
    build_dashboard.main()
    db_export.main()
    print("=" * 70)
    print("All scrapers finished. Review rows with:  python show_regulations.py")


if __name__ == "__main__":
    main()
