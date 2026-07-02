import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def build_email_html(top_jobs):
    """Build a simple email-friendly HTML table of today's top jobs."""
    rows = ""
    for job in top_jobs:
        rows += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{job.get('job_title', '')}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{job.get('employer_name', '')}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{job.get('match_percent', '')}%</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{job.get('h1b_signal', '')}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">
                <a href="{job.get('apply_link', '#')}">Apply →</a>
                {f'<br><a href="file://{job.get("tailored_resume_path")}">📄 Tailored CV</a>' if job.get('tailored_resume_path') else ''}
            </td>
        </tr>
        """

    return f"""
    <html>
    <body style="font-family: -apple-system, Arial, sans-serif;">
        <h2>Today's Top {len(top_jobs)} Job Matches</h2>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="background:#24292f; color:white;">
                <th style="padding:8px; text-align:left;">Title</th>
                <th style="padding:8px; text-align:left;">Company</th>
                <th style="padding:8px; text-align:left;">Match %</th>
                <th style="padding:8px; text-align:left;">H1B Signal</th>
                <th style="padding:8px; text-align:left;">Link</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """


def send_job_email(top_jobs):
    """Send the daily job report via Gmail SMTP."""
    if not top_jobs:
        subject = "Job Hunter — No new matches today"
        body_html = "<p>No jobs met the 75%+ match bar today. Better luck tomorrow.</p>"
    else:
        subject = f"Job Hunter — {len(top_jobs)} new matches today"
        body_html = build_email_html(top_jobs)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS  # sending to yourself

    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, GMAIL_ADDRESS, msg.as_string())
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    # Quick test with fake data, no need to run the full pipeline
    test_jobs = [
        {
            "job_title": "Test AI Engineer",
            "employer_name": "Test Co",
            "match_percent": 88,
            "h1b_signal": "Unknown: No clear signal either way",
            "apply_link": "https://example.com",
        }
    ]
    send_job_email(test_jobs)