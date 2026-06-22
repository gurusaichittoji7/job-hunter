import re

# Only the clearly-too-senior titles get auto-excluded regardless of years stated
HARD_EXCLUDE_TITLES = [
    "staff", "principal", "director", "vp", "vice president",
    "head of", "distinguished", "chief",
]

MAX_YEARS = 5


def is_hard_excluded_title(title):
    title_lower = (title or "").lower()
    return any(kw in title_lower for kw in HARD_EXCLUDE_TITLES)


def exceeds_year_requirement(description):
    """
    Look for patterns like '8+ years', '10+ years of experience', etc.
    Returns True if the JD requires more than MAX_YEARS.
    """
    if not description:
        return False

    patterns = re.findall(r"(\d{1,2})\+?\s*(?:to\s*\d{1,2})?\s*years", description.lower())
    for years_str in patterns:
        years = int(years_str)
        if years > MAX_YEARS:
            return True
    return False


def is_mid_level(job):
    """Return True if this job looks like a 0-5 years / mid-level role."""
    title = job.get("job_title", "")
    description = job.get("job_description", "")

    if is_hard_excluded_title(title):
        return False
    if exceeds_year_requirement(description):
        return False
    return True


def filter_mid_level_jobs(jobs):
    """Keep only jobs that look like 0-5 years experience."""
    return [job for job in jobs if is_mid_level(job)]


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs

    jobs = fetch_all_jobs()
    print(f"Total jobs fetched: {len(jobs)}")

    mid_level = filter_mid_level_jobs(jobs)
    print(f"Mid-level (0-5 yrs) jobs: {len(mid_level)}\n")

    for job in mid_level[:10]:
        print(job.get("job_title"), "-", job.get("employer_name"))