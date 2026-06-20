import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "seen_jobs.db")


def init_db():
    """Create the seen_jobs table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            job_id TEXT PRIMARY KEY,
            job_title TEXT,
            employer_name TEXT,
            apply_link TEXT,
            first_seen TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_job_id(job):
    """
    Build a unique ID for a job.
    Prefer the API's own job_id; fallback to apply_link if missing.
    """
    return job.get("job_id") or job.get("job_apply_link")


def filter_new_jobs(jobs):
    """
    Given a list of jobs from fetch_jsearch, return only the ones
    we haven't seen before, and mark them as seen.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    new_jobs = []
    for job in jobs:
        jid = get_job_id(job)
        if not jid:
            continue

        cursor.execute("SELECT 1 FROM seen_jobs WHERE job_id = ?", (jid,))
        if cursor.fetchone() is None:
            new_jobs.append(job)
            cursor.execute(
                "INSERT INTO seen_jobs (job_id, job_title, employer_name, apply_link, first_seen) "
                "VALUES (?, ?, ?, ?, datetime('now'))",
                (
                    jid,
                    job.get("job_title"),
                    job.get("employer_name"),
                    job.get("job_apply_link"),
                ),
            )

    conn.commit()
    conn.close()
    return new_jobs


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs

    jobs = fetch_all_jobs()
    print(f"Fetched {len(jobs)} total jobs")

    new_jobs = filter_new_jobs(jobs)
    print(f"New (never-seen) jobs: {len(new_jobs)}")

    for job in new_jobs[:5]:
        print(job.get("job_title"), "-", job.get("employer_name"))
        print(job.get("job_apply_link"))
        print("---")