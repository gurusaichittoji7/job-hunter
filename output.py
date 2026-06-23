import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def generate_html(scored_jobs):
    """Build an HTML report from scored jobs, sorted by match% descending."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    sorted_jobs = sorted(scored_jobs, key=lambda j: j.get("match_percent") or 0, reverse=True)

    rows = ""
    for job in sorted_jobs:
        verdict = job.get("verdict", "Skip")
        verdict_color = "#1a7f37" if verdict == "Apply" else "#d1242f"
        match_percent = job.get("match_percent", 0)

        rows += f"""
        <tr>
            <td>{job.get('job_title', '')}</td>
            <td>{job.get('employer_name', '')}</td>
            <td>{match_percent}%</td>
            <td style="color:{verdict_color}; font-weight:bold;">{verdict}</td>
            <td>{job.get('h1b_signal', '')}</td>
            <td>{job.get('reason', '')}</td>
            <td>{job.get('source', '')}</td>
            <td><a href="{job.get('apply_link', '#')}" target="_blank">Apply →</a></td>        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Job Hunter Results</title>
        <style>
            body {{ font-family: -apple-system, Arial, sans-serif; margin: 30px; background: #f6f8fa; }}
            h1 {{ color: #24292f; }}
            table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            th, td {{ padding: 10px 14px; border-bottom: 1px solid #d0d7de; text-align: left; font-size: 14px; vertical-align: top; }}
            th {{ background: #24292f; color: white; position: sticky; top: 0; }}
            tr:hover {{ background: #f0f3f6; }}
            a {{ color: #0969da; text-decoration: none; font-weight: 600; }}
            .meta {{ color: #57606a; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>Job Hunter Results</h1>
        <p class="meta">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Total new jobs: {len(sorted_jobs)}</p>
        <table>
            <tr>
                <th>Title</th>
                <th>Company</th>
                <th>Match %</th>
                <th>Verdict</th>
                <th>H1B Signal</th>
                <th>Reason</th>
                <th>Link</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"jobs_{timestamp}.html")

    with open(filepath, "w") as f:
        f.write(html)

    return filepath


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs
    from dedupe import filter_new_jobs
    from score import score_jobs

    jobs = fetch_all_jobs()
    new_jobs = filter_new_jobs(jobs)
    print(f"Scoring {len(new_jobs)} new jobs...")

    scored = score_jobs(new_jobs)
    filepath = generate_html(scored)

    print(f"\nDone! Report saved to: {filepath}")