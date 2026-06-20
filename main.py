import webbrowser
from fetch_jsearch import fetch_all_jobs
from dedupe import filter_new_jobs
from score import score_jobs
from output import generate_html


def run():
    print("=" * 50)
    print("JOB HUNTER — starting run")
    print("=" * 50)

    print("\n[1/4] Fetching jobs across all roles...")
    jobs = fetch_all_jobs()
    print(f"      → {len(jobs)} jobs fetched")

    print("\n[2/4] Filtering out previously seen jobs...")
    new_jobs = filter_new_jobs(jobs)
    print(f"      → {len(new_jobs)} new jobs to evaluate")

    if not new_jobs:
        print("\nNo new jobs found this run. Nothing to report.")
        return

    print(f"\n[3/4] Scoring {len(new_jobs)} jobs against your resume...")
    scored = score_jobs(new_jobs)
    print("      → scoring complete")

    print("\n[4/4] Generating report...")
    filepath = generate_html(scored)
    print(f"      → saved to {filepath}")

    print("\nOpening report in browser...")
    webbrowser.open(f"file://{filepath}")

    print("\n" + "=" * 50)
    print("DONE")
    print("=" * 50)


if __name__ == "__main__":
    run()