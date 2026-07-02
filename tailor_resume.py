import os
import re
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
RESUME_PATH = os.path.join(os.path.dirname(__file__), "resume.txt")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "resumes")

MAX_TAILORED = 5
MIN_MATCH_FOR_TAILOR = 80
JD_CHARS_FOR_TAILOR = 500


def load_resume():
    with open(RESUME_PATH, "r") as f:
        return f.read()


def tailor_summary_with_claude(resume_text, job):
    """Only tailor the summary — everything else stays identical."""
    prompt = f"""You are a professional resume writer. Write a tailored 2-3 sentence professional summary for this candidate applying to the job below. Keep all facts accurate — do not invent experience. Match keywords from the job description naturally.

CANDIDATE BACKGROUND:
{resume_text[:1500]}

JOB TITLE: {job.get('job_title')}
COMPANY: {job.get('employer_name')}
JOB DESCRIPTION:
{(job.get('job_description') or '')[:JD_CHARS_FOR_TAILOR]}

Return ONLY the summary text, no JSON, no preamble, no markdown. Just 2-3 sentences."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def generate_pdf(job, tailored_summary):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    safe_name = re.sub(r"[^\w\s-]", "", f"{job.get('job_title', 'role')}_{job.get('employer_name', 'company')}")
    safe_name = re.sub(r"\s+", "_", safe_name)[:60]
    filepath = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    # ── Styles ──────────────────────────────────────────────
    def S(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    name_s = S("name", fontSize=16, fontName="Helvetica-Bold", alignment=1, spaceAfter=2)
    contact_s = S("contact", fontSize=8.5, fontName="Helvetica", alignment=1, spaceAfter=6)
    section_s = S("section", fontSize=10, fontName="Helvetica-Bold", spaceBefore=7, spaceAfter=1)
    body_s = S("body", fontSize=8.5, fontName="Helvetica", spaceAfter=3, leading=12)
    skill_s = S("skill", fontSize=8.5, fontName="Helvetica", spaceAfter=2, leading=12)
    exp_title_s = S("exptitle", fontSize=9, fontName="Helvetica-Bold", spaceBefore=5, spaceAfter=1)
    bullet_s = S("bullet", fontSize=8.5, fontName="Helvetica", spaceAfter=1.5, leftIndent=12, leading=12)
    proj_name_s = S("projname", fontSize=8.5, fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=1)
    edu_s = S("edu", fontSize=8.5, fontName="Helvetica", spaceAfter=2, leading=12)

    def hr():
        return HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=4)

    def section(title):
        return [Paragraph(title, section_s), hr()]

    def exp_header(title, company, location, dates):
        left = f"<b>{title} | {company} | {location}</b>"
        right = dates
        data = [[Paragraph(left, exp_title_s), Paragraph(right, S("dr", fontSize=8.5, fontName="Helvetica", alignment=2))]]
        t = Table(data, colWidths=[4.8 * inch, 2.1 * inch])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        return t

    def bullet(text):
        return Paragraph(f"• {text}", bullet_s)

    story = []

    # ── HEADER ──────────────────────────────────────────────
    story.append(Paragraph("GURUSAI CHITTOJI", name_s))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(
        "gurusaic3x@gmail.com | +1 (503) 380-1422 | CA, USA | ",
        contact_s
    ))

    # ── SUMMARY ─────────────────────────────────────────────
    story += section("SUMMARY")
    story.append(Paragraph(tailored_summary, body_s))

    # ── SKILLS ──────────────────────────────────────────────
    story += section("SKILLS")

    skills = [
        ("Machine Learning & AI", "Classical ML, LLM-Based Applications, Generative AI, Agentic AI Workflows, Multi-Agent Systems, RAG Pipelines, Forecasting, Optimization, Decision Support Systems"),
        ("MLOps & Deployment", "CI/CD Pipelines (GitHub Actions), Docker, Containerized Deployments, Model Monitoring, Production Deployment, MLOps Practices, Cloud Infrastructure, Version Control (Git)"),
        ("Cloud Platforms", "AWS (EC2, S3, Lambda, RDS), GCP, Azure, Firebase, Supabase, Distributed Computing, Scalable System Architecture"),
        ("Python & ML Libraries", "PyTorch, TensorFlow, Hugging Face Transformers, Scikit-Learn, Pandas, NumPy, FastEmbed, Sentence-Transformers"),
        ("LLM & Agentic Systems", "LangChain, LangGraph, FAISS, Pinecone, Vector Embeddings, Semantic Search, Prompt Engineering, Human-in-the-Loop Checkpointing"),
        ("Backend Engineering", "FastAPI, RESTful APIs, Python, Middleware Architecture, Real-Time Processing, PostgreSQL, MongoDB, SQL/NoSQL Databases"),
        ("Observability & Monitoring", "Real-Time Telemetry, Execution Trace Capture, Token Usage Monitoring, Performance Tracking, SQLite Query Logging, Model Performance Dashboards"),
    ]
    for label, content in skills:
        story.append(Paragraph(f"<b>{label}:</b> {content}", skill_s))

    # ── EXPERIENCE ──────────────────────────────────────────
    story += section("EXPERIENCE")

    story.append(exp_header("AI/ML Engineer & Researcher", "Self Employed", "CA, USA", "Nov 2025 – Present"))
    for b in [
        "Designed and deployed end-to-end LLM-based RAG pipeline with FAISS achieving 92% retrieval accuracy across 300+ documents with real-time monitoring dashboards tracking confidence scores and cache metrics",
        "Built production semantic routing middleware reducing inference costs through dynamic model selection and sub-10ms cache response times using vector database similarity matching",
        "Developed LangGraph observability tool capturing full execution traces and state transitions enabling time-travel debugging for multi-agent workflows with inline modification capabilities",
    ]:
        story.append(bullet(b))

    story.append(exp_header("Software Engineer", "One Community Global", "San Gabriel, CA", "Jun 2025 – Oct 2025"))
    for b in [
        "Collaborated with cross-functional teams implementing JavaScript-based features with unit testing and CI/CD integration",
        "Contributed to platform scalability improvements and code quality standards through peer reviews and documentation",
        "Delivered maintainable solutions for automation and user-facing applications across business domains",
    ]:
        story.append(bullet(b))

    story.append(exp_header("AI/ML Engineer", "Neolytix", "India (Hybrid)", "Aug 2021 – Aug 2023"))
    for b in [
        "Built and deployed classical ML models for forecasting and optimization solving real-world business problems with measurable accuracy improvements",
        "Developed scalable data pipelines and ETL workflows processing large datasets with Python TensorFlow and cloud infrastructure",
        "Collaborated with product and business stakeholders translating requirements into production-ready ML solutions with monitoring and deployment automation",
        "Presented model insights and recommendations through dashboards communicating technical tradeoffs to non-technical audiences",
    ]:
        story.append(bullet(b))

    story.append(exp_header("Python Engineer", "Neolytix", "India (Hybrid)", "May 2021 – Jul 2021"))
    for b in [
        "Engineered Python-based automation solutions and data processing pipelines with TensorFlow integrations",
        "Implemented feature engineering and model experimentation workflows supporting ML system development",
    ]:
        story.append(bullet(b))

    story.append(exp_header("Python Engineer Trainee", "JSpiders", "Bengaluru, India", "Aug 2020 – Apr 2021"))
    for b in [
        "Completed intensive training in Python programming machine learning fundamentals and software engineering practices",
        "Developed foundational skills in classical ML algorithms data structures and problem-solving techniques",
    ]:
        story.append(bullet(b))

    # ── PROJECTS ────────────────────────────────────────────
    story += section("PROJECTS")

    projects = [
        ("MediQuery RAG – Clinical AI Assistant",
         "Engineered production RAG system using FAISS with all-MiniLM-L6-v2 embeddings querying 300+ medical documents achieving grounded low-hallucination outputs with ICD-11 mapping and real-time admin dashboard tracking retrieval confidence scores query logs and cache metrics with 1-hour TTL deployed using Docker and CI/CD practices"),
        ("Chronos – Agent Flight Recorder & Time-Travel Debugger",
         "Built LangGraph observability tool capturing full execution traces tool invocations and state transitions across multi-agent workflows with React Flow visualization enabling time-travel debugging allowing engineers to modify inline JSON prompts and resume live pipeline execution for production troubleshooting"),
        ("Semantic Router & Inference Optimizer",
         "Developed intelligent middleware using vector database semantic cache matching achieving sub-10ms query response dynamically routing low-complexity queries to lightweight models and reserving heavy reasoning models for advanced tasks reducing enterprise API costs through optimized model selection logic"),
        ("Multi-Agent Research Engine",
         "Designed stateful multi-agent system using LangGraph with Planner-Researcher-Writer execution nodes implementing Human-in-the-Loop checkpointing pausing for human validation before expensive web searches solving black-box AI workflow problems with predictable quality output and cost control"),
        ("Carvia – AI Resume Customization Platform",
         "Architected full-stack platform using FastAPI React Supabase PostgreSQL and Google OAuth executing automated resume tailoring workflows with state management file-generation engines and GitHub Actions CI/CD deployment demonstrating end-to-end software engineering and cloud integration capabilities"),
    ]

    for proj_name, proj_desc in projects:
        story.append(Paragraph(proj_name, proj_name_s))
        story.append(bullet(proj_desc))

    # ── EDUCATION ───────────────────────────────────────────
    story += section("EDUCATION")
    data = [[
        Paragraph("<b>Master of Science in Computer Science | University of Bridgeport, CT, USA</b>", edu_s),
        Paragraph("GPA: 3.4/4.0", S("gpa", fontSize=8.5, fontName="Helvetica", alignment=2))
    ]]
    t = Table(data, colWidths=[5.3 * inch, 1.6 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(t)

    # ── CERTIFICATIONS ──────────────────────────────────────
    story += section("CERTIFICATIONS")
    certs = [
        "Google AI Essentials – Google",
        "MLOps for Generative AI",
        "Project Management Foundations – LinkedIn Learning",
        "What Is Generative AI? – LinkedIn Learning",
    ]
    for c in certs:
        story.append(Paragraph(c, skill_s))

    doc.build(story)
    return filepath


def tailor_and_generate(jobs):
    resume_text = load_resume()
    results = []

    eligible = [
        j for j in jobs
        if (j.get("match_percent") or 0) >= MIN_MATCH_FOR_TAILOR
    ][:MAX_TAILORED]

    print(f"  Tailoring resumes for {len(eligible)} top jobs (of {len(jobs)} total)...")

    for job in jobs:
        if job in eligible:
            print(f"  → Tailoring: {job.get('job_title')} - {job.get('employer_name')}")
            tailored_summary = tailor_summary_with_claude(resume_text, job)
            pdf_path = generate_pdf(job, tailored_summary)
            job["tailored_resume_path"] = pdf_path
        else:
            job["tailored_resume_path"] = None
        results.append(job)

    return results


if __name__ == "__main__":
    test_job = {
        "job_title": "LLM Engineer",
        "employer_name": "Anthropic",
        "job_description": "Looking for an LLM Engineer with RAG, LangChain, FastAPI, and production deployment experience.",
        "apply_link": "https://example.com",
        "match_percent": 88,
    }
    resume_text = load_resume()
    tailored_summary = tailor_summary_with_claude(resume_text, test_job)
    path = generate_pdf(test_job, tailored_summary)
    print(f"PDF generated: {path}")
    import subprocess
    subprocess.run(["open", path])