from collections import defaultdict

MIN_MATCH_PERCENT = 75
MAX_PER_COMPANY = 2
TOP_N = 50


def select_top_jobs(scored_jobs):
    """
    Filter to jobs with match% >= 75, cap at 2 per company,
    then return the top 50 overall sorted by match%.
    """
    # Only consider jobs that meet the minimum bar
    eligible = [j for j in scored_jobs if (j.get("match_percent") or 0) >= MIN_MATCH_PERCENT]

    # Sort by match% descending first, so when we cap per-company,
    # we keep each company's BEST matches, not arbitrary ones
    eligible.sort(key=lambda j: j.get("match_percent") or 0, reverse=True)

    company_counts = defaultdict(int)
    diversified = []

    for job in eligible:
        company = job.get("employer_name", "unknown")
        if company_counts[company] < MAX_PER_COMPANY:
            diversified.append(job)
            company_counts[company] += 1

    # Final cut to top 50 overall (already sorted by match%)
    return diversified[:TOP_N]


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs
    from fetch_company_boards import fetch_all_company_boards
    from filter_experience import filter_mid_level_jobs
    from dedupe import filter_new_jobs
    from enrich_direct_links import enrich_all
    from score import score_jobs

    jsearch_jobs = fetch_all_jobs()
    company_jobs = fetch_all_company_boards()
    all_jobs = jsearch_jobs + company_jobs

    mid_level = filter_mid_level_jobs(all_jobs)
    new_jobs = filter_new_jobs(mid_level)

    print(f"Scoring {len(new_jobs)} jobs...")
    enriched = enrich_all(new_jobs)
    scored = score_jobs(enriched)

    top_jobs = select_top_jobs(scored)
    print(f"\nTop {len(top_jobs)} jobs (75%+, max 2/company):\n")
    for job in top_jobs:
        print(f"{job['match_percent']}% - {job['job_title']} - {job['employer_name']}")