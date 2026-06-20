import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAPIDAPI_KEY")
BASE_URL = "https://jsearch.p.rapidapi.com/search"


def fetch_jobs(query, location="United States", num_pages=1):
    """
    Fetch jobs from JSearch API.
    query: e.g. "Machine Learning Engineer"
    location: e.g. "United States"
    """
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
        print(f"Error: {response.status_code} - {response.text}")
        return []

    data = response.json()
    return data.get("data", [])


if __name__ == "__main__":
    jobs = fetch_jobs("Machine Learning Engineer")
    print(f"Found {len(jobs)} jobs\n")
    for job in jobs[:5]:
        print(job.get("job_title"), "-", job.get("employer_name"))
        print(job.get("job_apply_link"))
        print("---")