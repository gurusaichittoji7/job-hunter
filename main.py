import webbrowser
from fetch_jsearch import fetch_all_jobs
from fetch_company_boards import fetch_all_company_boards
from filter_experience import filter_mid_level_jobs
from dedupe import filter_new_jobs
from enrich_direct_links import enrich_all
from score import score_jobs
from output import generate_html


def run():
    print("=" * 50)
    print("JOB HUNTER — starting run")
    print("=" * 50)

    print("\n[1/6] Fetching jobs across all roles...")
    jsearch_jobs = fetch_all_jobs()
    print(f"      → {len(jsearch_jobs)} jobs fetched from JSearch")

    print("\n[2/6] Checking target companies' direct job boards...")
    company_jobs = fetch_all_company_boards()
    print(f"      → {len(company_jobs)} relevant jobs found across target companies")

    all_jobs = jsearch_jobs + company_jobs
    print(f"      → {len(all_jobs)} total jobs combined")

    print("\n[3/6] Filtering to mid-level (0-5 yrs) roles...")
    mid_level_jobs = filter_mid_level_jobs(all_jobs)
    print(f"      → {len(mid_level_jobs)} mid-level jobs remain")

    print("\n[4/6] Filtering out previously seen jobs...")
    new_jobs = filter_new_jobs(mid_level_jobs)
    print(f"      → {len(new_jobs)} new jobs to evaluate")

    if not new_jobs:
        print("\nNo new jobs found this run. Nothing to report.")
        return

    print(f"\n[5/6] Checking for direct company apply links...")
    enriched_jobs = enrich_all(new_jobs)
    print("      → enrichment complete")

    print(f"\n[6/6] Scoring {len(enriched_jobs)} jobs against your resume...")
    scored = score_jobs(enriched_jobs)
    print("      → scoring complete")

    print("\nGenerating report...")
    filepath = generate_html(scored)
    print(f"      → saved to {filepath}")

    print("\nOpening report in browser...")
    webbrowser.open(f"file://{filepath}")

    print("\n" + "=" * 50)
    print("DONE")
    print("=" * 50)


if __name__ == "__main__":
    run()