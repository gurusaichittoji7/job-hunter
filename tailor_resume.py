import os
import re
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

MAX_TAILORED = 5        # only tailor top N jobs
MIN_MATCH_FOR_TAILOR = 80  # only tailor if match% is strong enough
JD_CHARS_FOR_TAILOR = 500  # only send first 500 chars of JD to Claude

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
RESUME_PATH = os.path.join(os.path.dirname(__file__), "resume.txt")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "resumes")


def load_resume():
    with open(RESUME_PATH, "r") as f:
        return f.read()


def tailor_resume_with_claude(resume_text, job):
    prompt = f"""You are a professional resume writer. Rewrite only the summary and highlight the most relevant skills/bullets from this resume for the job below. Keep all facts accurate — do not invent experience.

RESUME:
{resume_text}

JOB TITLE: {job.get('job_title')}
COMPANY: {job.get('employer_name')}
JOB DESCRIPTION (first paragraph):
{(job.get('job_description') or '')[:JD_CHARS_FOR_TAILOR]}

Return ONLY valid JSON, no preamble, no markdown:
{{"summary": "<2-3 sentence tailored summary>", "skills_highlight": ["<skill1>", "<skill2>", "<skill3>", "<skill4>", "<skill5>", "<skill6>"], "key_bullets": ["<bullet1>", "<bullet2>", "<bullet3>", "<bullet4>", "<bullet5>"]}}
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def generate_pdf(job, tailored):
    """Generate a clean PDF resume tailored for this specific job."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Safe filename from job title + company
    safe_name = re.sub(r"[^\w\s-]", "", f"{job.get('job_title', 'role')}_{job.get('employer_name', 'company')}")
    safe_name = re.sub(r"\s+", "_", safe_name)[:60]
    filepath = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle("name", fontSize=18, fontName="Helvetica-Bold", spaceAfter=2)
    contact_style = ParagraphStyle("contact", fontSize=9, fontName="Helvetica", textColor=colors.grey, spaceAfter=8)
    section_style = ParagraphStyle("section", fontSize=11, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#24292f"))
    body_style = ParagraphStyle("body", fontSize=9, fontName="Helvetica", spaceAfter=3, leading=14)
    bullet_style = ParagraphStyle("bullet", fontSize=9, fontName="Helvetica", spaceAfter=2, leftIndent=12, leading=13)

    story = []

    # Header
    story.append(Paragraph("Gurusai Chittoji", name_style))
    story.append(Paragraph(
        "gurusaichittoji7@gmail.com  |  linkedin.com/in/gurusai-chittoji-73a5a822a  |  github.com/gurusaichittoji7",
        contact_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#24292f")))

    # Tailored Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    story.append(Paragraph(tailored.get("summary", ""), body_style))

    # Skills Highlight
    story.append(Paragraph("CORE SKILLS", section_style))
    skills = " • ".join(tailored.get("skills_highlight", []))
    story.append(Paragraph(skills, body_style))

    # Key Experience Bullets
    story.append(Paragraph("KEY EXPERIENCE HIGHLIGHTS", section_style))
    for bullet in tailored.get("key_bullets", []):
        story.append(Paragraph(f"• {bullet}", bullet_style))

    # Note at bottom
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Paragraph(
        f"<i>Tailored for: {job.get('job_title')} at {job.get('employer_name')}</i>",
        ParagraphStyle("note", fontSize=8, fontName="Helvetica-Oblique", textColor=colors.grey, spaceBefore=4)
    ))

    doc.build(story)
    return filepath


def tailor_and_generate(jobs):
    """Tailor resume and generate PDF for top qualifying jobs only."""
    resume_text = load_resume()
    results = []

    # Only tailor top N jobs that meet the match threshold
    eligible = [
        j for j in jobs
        if (j.get("match_percent") or 0) >= MIN_MATCH_FOR_TAILOR
    ][:MAX_TAILORED]

    print(f"  Tailoring resumes for {len(eligible)} top jobs (of {len(jobs)} total)...")

    for job in jobs:
        if job in eligible:
            print(f"  → Tailoring: {job.get('job_title')} - {job.get('employer_name')}")
            tailored = tailor_resume_with_claude(resume_text, job)
            if tailored:
                pdf_path = generate_pdf(job, tailored)
                job["tailored_resume_path"] = pdf_path
            else:
                job["tailored_resume_path"] = None
        else:
            job["tailored_resume_path"] = None
        results.append(job)

    return results


if __name__ == "__main__":
    test_job = {
        "job_title": "AI/ML Engineer",
        "employer_name": "Anthropic",
        "job_description": "We are looking for an AI/ML Engineer with experience in RAG pipelines, LangChain, FastAPI, and production LLM deployment.",
        "apply_link": "https://example.com"
    }
    resume_text = load_resume()
    tailored = tailor_resume_with_claude(resume_text, test_job)
    if tailored:
        path = generate_pdf(test_job, tailored)
        print(f"PDF generated: {path}")
    else:
        print("Failed to tailor resume")