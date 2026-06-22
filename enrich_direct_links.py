import requests

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
LEVER_URL = "https://api.lever.co/v0/postings/{slug}?mode=json"


def slugify(company_name):
    """Turn 'Tanium Inc.' into a likely slug like 'tanium'."""
    name = company_name.lower()
    for junk in [",", ".", "inc", "llc", "corp", "corporation", "company"]:
        name = name.replace(junk, "")
    return name.strip().replace(" ", "")


def check_greenhouse(slug, job_title):
    """Try to find a matching job on this company's Greenhouse board."""
    try:
        resp = requests.get(GREENHOUSE_URL.format(slug=slug), timeout=5)
        if resp.status_code != 200:
            return None
        jobs = resp.json().get("jobs", [])
        for job in jobs:
            if job_title.lower() in job.get("title", "").lower():
                return job.get("absolute_url")
    except requests.RequestException:
        return None
    return None


def check_lever(slug, job_title):
    """Try to find a matching job on this company's Lever board."""
    try:
        resp = requests.get(LEVER_URL.format(slug=slug), timeout=5)
        if resp.status_code != 200:
            return None
        jobs = resp.json()
        for job in jobs:
            if job_title.lower() in job.get("text", "").lower():
                return job.get("hostedUrl")
    except requests.RequestException:
        return None
    return None

def check_ashby(slug, job_title):
    """Try to find a matching job on this company's Ashby board."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        jobs = resp.json().get("jobs", [])
        for job in jobs:
            if job_title.lower() in job.get("title", "").lower():
                return job.get("jobUrl")
    except requests.RequestException:
        return None
    return None

def check_workable(slug, job_title):
    """Try to find a matching job on this company's Workable board."""
    url = f"https://apply.workable.com/api/v1/widget/accounts/{slug}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        jobs = resp.json().get("jobs", [])
        for job in jobs:
            if job_title.lower() in job.get("title", "").lower():
                shortcode = job.get("shortcode")
                return f"https://apply.workable.com/{slug}/j/{shortcode}/"
    except requests.RequestException:
        return None
    return None

def enrich_with_direct_link(job):
    """
    Try Greenhouse, Lever, Ashby, then Workable for a direct company link.
    If found, overwrite best_apply_link/best_apply_source with the direct one.
    """
    company = job.get("employer_name", "")
    title = job.get("job_title", "")
    slug = slugify(company)

    checks = [
        (check_greenhouse, "Greenhouse (direct)"),
        (check_lever, "Lever (direct)"),
        (check_ashby, "Ashby (direct)"),
        (check_workable, "Workable (direct)"),
    ]

    for check_fn, source_label in checks:
        direct_link = check_fn(slug, title)
        if direct_link:
            job["best_apply_link"] = direct_link
            job["best_apply_source"] = source_label
            break

    return job


def enrich_all(jobs):
    """Run enrichment on a list of jobs."""
    for job in jobs:
        enrich_with_direct_link(job)
    return jobs


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs
    from dedupe import filter_new_jobs

    jobs = fetch_all_jobs()
    new_jobs = filter_new_jobs(jobs)
    print(f"Checking {len(new_jobs)} jobs for direct company links...\n")

    enriched = enrich_all(new_jobs)
    for job in enriched:
        print(f"{job.get('job_title')} - {job.get('employer_name')}")
        print(f"Source: {job.get('best_apply_source')}")
        print(job.get('best_apply_link'))
        print("---")