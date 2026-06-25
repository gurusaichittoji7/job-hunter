from collections import defaultdict

MIN_MATCH_PERCENT = 75
MAX_PER_COMPANY = 2
TOP_N = 50

BLOCKED_SOURCES = {"talent.com", "learn4good", "trabajo.org", "theladders.com", "ladders", "mysmartpros", "digitalhire"}
BLOCKED_EMPLOYERS = {"quzara llc"}


def is_blocked(job):
    source = (job.get("source") or "").lower()
    employer = (job.get("employer_name") or "").lower()
    if any(blocked in source for blocked in BLOCKED_SOURCES):
        return True
    if any(blocked in employer for blocked in BLOCKED_EMPLOYERS):
        return True
    return False


def select_top_jobs(scored_jobs):
    """
    Filter to jobs with match% >= 75, exclude blocked sources/employers,
    cap at 2 per company, then return the top 50 overall sorted by match%.
    """
    eligible = [
        j for j in scored_jobs
        if (j.get("match_percent") or 0) >= MIN_MATCH_PERCENT and not is_blocked(j)
    ]

    eligible.sort(key=lambda j: j.get("match_percent") or 0, reverse=True)

    company_counts = defaultdict(int)
    diversified = []

    for job in eligible:
        company = job.get("employer_name", "unknown")
        if company_counts[company] < MAX_PER_COMPANY:
            diversified.append(job)
            company_counts[company] += 1

    return diversified[:TOP_N]