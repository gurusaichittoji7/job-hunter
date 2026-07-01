import requests

TIMEOUT = 6

EXPIRED_PHRASES = [
    "job is no longer available",
    "this job has expired",
    "position has been filled",
    "job listing has expired",
    "no longer accepting applications",
    "this position is no longer available",
    "job has been closed",
    "posting has expired",
    "this job is closed",
    "vacancy has been filled",
    "not currently accepting",
    "job is closed",
]

# Only validate links from sources we can reliably check without auth
VALIDATABLE_SOURCES = {
    "greenhouse (direct)", "lever (direct)", "ashby (direct)",
    "workable (direct)", "smartrecruiters (direct)", "bamboohr (direct)"
}

# Domains we know block unauthenticated requests — skip these entirely
SKIP_DOMAINS = [
    "linkedin.com", "indeed.com", "ziprecruiter.com", "glassdoor.com",
    "talent.com", "learn4good", "trabajo.org", "theladders.com",
    "lensa.com", "snagajob.com", "tietalent.com", "jobright.ai",
    "efinancialcareers.com", "salutemyjob.com", "recruit.net",
    "womenforhire.com", "aijobs.com", "jobserve.com",
]


def should_validate(job):
    """Only validate if it's a direct ATS link we can reliably check."""
    source = (job.get("source") or job.get("best_apply_source") or "").lower()
    url = (job.get("apply_link") or job.get("best_apply_link") or "").lower()

    if source in VALIDATABLE_SOURCES:
        return True
    if any(domain in url for domain in SKIP_DOMAINS):
        return False
    return False  # default: skip validation if unsure


def is_link_alive(url):
    """Check if a direct ATS link is still active."""
    if not url or url == "#":
        return False
    try:
        resp = requests.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resp.status_code in (404, 410):
            return False
        content_lower = resp.text.lower()
        if any(phrase in content_lower for phrase in EXPIRED_PHRASES):
            return False
        return True
    except requests.RequestException:
        return True  # keep on network errors, don't wrongly drop


def filter_active_jobs(jobs):
    """
    Remove jobs with confirmed-expired direct ATS links.
    Skip validation for LinkedIn/aggregator links — can't reliably check those.
    """
    active = []
    dropped = 0
    skipped_validation = 0

    for job in jobs:
        if should_validate(job):
            url = job.get("apply_link") or job.get("best_apply_link")
            if is_link_alive(url):
                active.append(job)
            else:
                dropped += 1
                print(f"  ✗ Expired: {job.get('job_title')} - {job.get('employer_name')}")
        else:
            # Can't validate — keep it, let the user judge
            active.append(job)
            skipped_validation += 1

    print(f"      → {dropped} expired direct links removed")
    print(f"      → {skipped_validation} links skipped validation (LinkedIn/aggregators)")
    print(f"      → {len(active)} jobs remain")
    return active


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs
    from dedupe import filter_new_jobs

    jobs = fetch_all_jobs()
    new_jobs = filter_new_jobs(jobs)
    print(f"Validating {len(new_jobs)} job links...\n")
    active = filter_active_jobs(new_jobs)
    print(f"\nFinal active jobs: {len(active)}")