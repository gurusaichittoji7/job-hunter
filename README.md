# Job Hunter

A personal job search agent that automatically finds, filters, and scores fresh AI/ML job postings, built to run with a single click.

## What it does

1. **Fetches** job postings across 10 target roles (Applied AI Engineer, LLM Engineer, AI/ML Engineer, etc.) using the JSearch API, which aggregates LinkedIn, Indeed, ZipRecruiter, Glassdoor, and Google for Jobs results.
2. **Filters** out anything older than 24 hours and anything already seen in a previous run (SQLite-backed deduplication).
3. **Enriches** each posting by checking if the company has a public Greenhouse or Lever job board, and swaps in a direct apply link when one exists — bypassing aggregator reposts.
4. **Scores** every new job against my resume using Claude, the way a real recruiter would: skill match, seniority fit, domain relevance. Each job gets a match %, an Apply/Skip verdict, and a one-line reason.
5. **Flags H1B sponsorship signals** by combining a JD keyword scan (catching nuance like "no new sponsorship, but transfers welcomed") with a known-frequent-sponsor company list.
6. **Generates** a clean, color-coded HTML report — sorted by match %, opened automatically in the browser.

## Why I built this

Manually checking LinkedIn, Indeed, and company career pages every day for new AI/ML postings was repetitive and easy to fall behind on. This automates the entire discovery → triage workflow into one click, so I only spend time on jobs worth applying to.

## Stack

- Python
- JSearch API (RapidAPI) — job aggregation
- Greenhouse / Lever public APIs — direct apply link enrichment
- Anthropic Claude API — resume-to-JD scoring
- SQLite — deduplication across runs
- HTML/CSS — report generation

## Setup

1. Clone the repo
2. `python3 -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Add a `.env` file with: RAPIDAPI_KEY=your_key
ANTHROPIC_API_KEY=your_key

5. Add your resume as plain text in `resume.txt`
6. Run via `python3 main.py` or double-click `run.command`

## Notes

- JSearch free tier allows 200 requests/month, each run uses 10-20 depending on results, so this is built for roughly daily use, not constant polling.
- H1B signal is a heuristic, not authoritative, absence of a "no sponsorship" flag doesn't guarantee a company sponsors.
- Greenhouse/Lever enrichment only works for companies using those specific ATS platforms; Workday and custom career sites aren't covered yet (no public API available).

