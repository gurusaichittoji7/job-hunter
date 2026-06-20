import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESUME_PATH = os.path.join(os.path.dirname(__file__), "resume.txt")

# Lightweight known-sponsor signal — not authoritative, just a quick heuristic
KNOWN_H1B_SPONSORS = {
    "google", "microsoft", "amazon", "meta", "apple", "ibm", "infosys",
    "tcs", "cognizant", "deloitte", "accenture", "capgemini", "oracle",
    "salesforce", "intel", "cisco", "qualcomm", "nvidia", "wipro",
    "tata consultancy services", "jpmorgan", "goldman sachs", "walmart",
    "uber", "linkedin", "adobe", "sap", "vmware", "dell"
}

NO_SPONSOR_KEYWORDS = [
    "no sponsorship", "not provide sponsorship", "unable to sponsor",
    "must be authorized to work", "without sponsorship",
    "us citizens only", "citizens or permanent residents",
    "no visa sponsorship", "not sponsor employment"
]


def load_resume():
    with open(RESUME_PATH, "r") as f:
        return f.read()


def check_h1b_signal(job_description, employer_name):
    """Combine keyword scan + known sponsor list for a quick H1B signal."""
    desc_lower = (job_description or "").lower()
    employer_lower = (employer_name or "").lower()

    keyword_flag = any(kw in desc_lower for kw in NO_SPONSOR_KEYWORDS)
    known_sponsor = any(name in employer_lower for name in KNOWN_H1B_SPONSORS)

    if keyword_flag:
        return "Risk: JD explicitly excludes sponsorship"
    elif known_sponsor:
        return "Likely OK: Known frequent H1B sponsor"
    else:
        return "Unknown: No clear signal either way"


def score_job_with_claude(resume_text, job):
    """Ask Claude to evaluate match % and Apply/Skip verdict."""
    job_title = job.get("job_title", "")
    employer = job.get("employer_name", "")
    description = job.get("job_description", "")

    prompt = f"""You are an experienced technical recruiter evaluating a candidate's resume against a job description.

RESUME:
{resume_text}

JOB TITLE: {job_title}
COMPANY: {employer}
JOB DESCRIPTION:
{description}

Evaluate the fit the way a recruiter actually would: overall skill match, seniority match, domain relevance.

Respond ONLY with valid JSON, no preamble, no markdown, in this exact format:
{{"match_percent": <integer 0-100>, "verdict": "Apply" or "Skip", "reason": "<one sentence reason>"}}
"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {"match_percent": 0, "verdict": "Skip", "reason": "Could not parse evaluation"}

    return result


def score_jobs(jobs):
    """Score a list of jobs against the resume, attach results."""
    resume_text = load_resume()
    scored_jobs = []

    for job in jobs:
        evaluation = score_job_with_claude(resume_text, job)
        h1b_signal = check_h1b_signal(job.get("job_description"), job.get("employer_name"))

        scored_jobs.append({
            "job_title": job.get("job_title"),
            "employer_name": job.get("employer_name"),
            "apply_link": job.get("job_apply_link"),
            "match_percent": evaluation.get("match_percent"),
            "verdict": evaluation.get("verdict"),
            "reason": evaluation.get("reason"),
            "h1b_signal": h1b_signal,
        })

    return scored_jobs


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs
    from dedupe import filter_new_jobs

    jobs = fetch_all_jobs()
    new_jobs = filter_new_jobs(jobs)
    print(f"Scoring {len(new_jobs)} new jobs...\n")

    scored = score_jobs(new_jobs)
    for job in scored[:5]:
        print(f"{job['job_title']} - {job['employer_name']}")
        print(f"Match: {job['match_percent']}% | Verdict: {job['verdict']}")
        print(f"H1B: {job['h1b_signal']}")
        print(f"Reason: {job['reason']}")
        print(job['apply_link'])
        print("---")