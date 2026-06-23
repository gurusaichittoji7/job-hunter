import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
BASE_URL = "https://jsearch.p.rapidapi.com/search"

ROLES = [
    "Applied AI Engineer",
    "AI/ML Engineer",
    "LLM Engineer",
    "Generative AI Engineer",
    "Machine Learning Engineer",
    "AI Infrastructure Engineer",
    "RAG Engineer",
    "NLP Engineer",
    "AI Platform Engineer",
    "AI Systems Engineer",
]


def is_within_last_24_hours(job):
    """Backup check: confirm job's posted timestamp is within last 24hrs."""
    posted_ts = job.get("job_posted_at_timestamp")
    if not posted_ts:
        return True  # if API doesn't give a timestamp, don't drop it
    posted_time = datetime.fromtimestamp(posted_ts, tz=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    return posted_time >= cutoff


def fetch_jobs_for_role(query, location="United States", num_pages=1):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{query} in {location}",
        "page": "1",
        "num_pages": str(num_pages),
        "date_posted": "today"
    }

    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error fetching '{query}': {response.status_code} - {response.text}")
        return []

    data = response.json()
    jobs = data.get("data", [])
    filtered = [job for job in jobs if is_within_last_24_hours(job)]
    for job in filtered:
        best_link, best_source = get_best_apply_link(job)
        job["best_apply_link"] = best_link
        job["best_apply_source"] = best_source

    return filtered
    return [job for job in jobs if is_within_last_24_hours(job)]

def get_best_apply_link(job):
    """Prefer a direct company application link over indirect reposts."""
    options = job.get("apply_options") or []
    direct = [opt for opt in options if opt.get("is_direct")]
    if direct:
        return direct[0]["apply_link"], direct[0]["publisher"]
    # fallback to whatever the default apply link is
    return job.get("job_apply_link"), job.get("job_publisher")

def fetch_all_jobs(location="United States"):
    """Loop through all target roles and collect fresh jobs."""
    all_jobs = []
    for role in ROLES:
        print(f"Searching: {role}...")
        jobs = fetch_jobs_for_role(role, location)
        all_jobs.extend(jobs)
    return all_jobs


if __name__ == "__main__":
    jobs = fetch_all_jobs()
    print(f"\nTotal jobs found across all roles: {len(jobs)}\n")
    for job in jobs[:5]:
        print(job.get("job_title"), "-", job.get("employer_name"))
        print(job.get("job_apply_link"))
        print("---")

if __name__ == "__main__":
    jobs = fetch_all_jobs()
    print(f"\nTotal jobs found across all roles: {len(jobs)}\n")
    import json
    print(json.dumps(jobs[0], indent=2))  # full raw structure of one job