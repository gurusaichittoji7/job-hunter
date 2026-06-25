import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RESUME_PATH = os.path.join(os.path.dirname(__file__), "resume.txt")

BATCH_SIZE = 8  # how many jobs to evaluate per Claude call

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
    desc_lower = (job_description or "").lower()
    employer_lower = (employer_name or "").lower()

    transfer_ok = "transfer" in desc_lower and ("h1b" in desc_lower or "h-1b" in desc_lower)
    keyword_flag = any(kw in desc_lower for kw in NO_SPONSOR_KEYWORDS)
    known_sponsor = any(name in employer_lower for name in KNOWN_H1B_SPONSORS)

    if keyword_flag and transfer_ok:
        return "Mixed: No new sponsorship, but H1B transfers welcomed"
    elif keyword_flag:
        return "Risk: JD explicitly excludes sponsorship"
    elif known_sponsor:
        return "Likely OK: Known frequent H1B sponsor"
    else:
        return "Unknown: No clear signal either way"


def score_batch_with_claude(resume_text, jobs_batch):
    """Score a batch of jobs in a single Claude call, resume sent once."""
    job_blocks = ""
    for i, job in enumerate(jobs_batch):
        job_blocks += f"""
JOB {i}:
TITLE: {job.get('job_title', '')}
COMPANY: {job.get('employer_name', '')}
DESCRIPTION: {(job.get('job_description') or '')[:1500]}
---
"""

    prompt = f"""You are an experienced technical recruiter evaluating a candidate's resume against multiple job descriptions.

RESUME:
{resume_text}

Evaluate EACH job below the way a recruiter actually would: overall skill match, seniority match, domain relevance.

{job_blocks}

Respond ONLY with valid JSON, no preamble, no markdown. Return a JSON array with one object per job, in the same order, in this exact format:
[{{"match_percent": <integer 0-100>, "verdict": "Apply" or "Skip", "reason": "<one sentence reason>"}}, ...]
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        results = json.loads(text)
    except json.JSONDecodeError:
        results = [{"match_percent": 0, "verdict": "Skip", "reason": "Could not parse evaluation"} for _ in jobs_batch]

    # Defensive: pad/truncate if Claude returns mismatched count
    while len(results) < len(jobs_batch):
        results.append({"match_percent": 0, "verdict": "Skip", "reason": "Missing evaluation"})

    return results[:len(jobs_batch)]


def score_jobs(jobs):
    """Score all jobs in batches, attach results."""
    resume_text = load_resume()
    scored_jobs = []

    for i in range(0, len(jobs), BATCH_SIZE):
        batch = jobs[i:i + BATCH_SIZE]
        evaluations = score_batch_with_claude(resume_text, batch)

        for job, evaluation in zip(batch, evaluations):
            h1b_signal = check_h1b_signal(job.get("job_description"), job.get("employer_name"))
            scored_jobs.append({
                "job_title": job.get("job_title"),
                "employer_name": job.get("employer_name"),
                "apply_link": job.get("best_apply_link", job.get("job_apply_link")),
                "source": job.get("best_apply_source", job.get("job_publisher")),
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
    print(f"Scoring {len(new_jobs)} new jobs in batches of {BATCH_SIZE}...\n")

    scored = score_jobs(new_jobs)
    for job in scored[:5]:
        print(f"{job['job_title']} - {job['employer_name']}")
        print(f"Match: {job['match_percent']}% | Verdict: {job['verdict']}")
        print(f"H1B: {job['h1b_signal']}")
        print(f"Reason: {job['reason']}")
        print(job['apply_link'])
        print("---")