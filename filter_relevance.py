SKILL_KEYWORDS = [
    # LLM & Agentic AI
    "rag", "retrieval-augmented generation", "retrieval augmented generation",
    "langchain", "langgraph", "multi-agent", "agentic", "agent",
    "human-in-the-loop", "hitl", "prompt engineering", "vector embeddings",
    "embeddings", "semantic search", "faiss", "pinecone",

    # ML/AI Core
    "pytorch", "tensorflow", "hugging face", "transformers",
    "scikit-learn", "sklearn", "pandas", "numpy",
    "sentence-transformers", "fastembed", "forecasting", "optimization",
    "machine learning", "deep learning",

    # Backend/Engineering
    "python", "fastapi", "restful api", "rest api", "postgresql",
    "mongodb", "docker", "ci/cd", "github actions",

    # Cloud
    "aws", "ec2", "lambda", "gcp", "azure",

    # Observability/MLOps
    "mlops", "model monitoring", "token usage", "production deployment",
    "llm", "large language model", "generative ai", "nlp",
]

MIN_KEYWORD_MATCHES = 3

def count_skill_matches(text):
    text_lower = (text or "").lower()
    return sum(1 for kw in SKILL_KEYWORDS if kw in text_lower)


def is_relevant_to_resume(job):
    """
    Cheap local pre-screen: does this job's title+description
    overlap meaningfully with my actual skill set?
    """
    combined_text = f"{job.get('job_title', '')} {job.get('job_description', '')}"
    return count_skill_matches(combined_text) >= MIN_KEYWORD_MATCHES


def filter_relevant_jobs(jobs):
    """Keep only jobs with enough skill-keyword overlap to be worth scoring."""
    return [job for job in jobs if is_relevant_to_resume(job)]


if __name__ == "__main__":
    from fetch_jsearch import fetch_all_jobs

    jobs = fetch_all_jobs()
    print(f"Total jobs fetched: {len(jobs)}")

    relevant = filter_relevant_jobs(jobs)
    print(f"Jobs passing relevance pre-screen: {len(relevant)}\n")

    for job in relevant[:10]:
        print(job.get("job_title"), "-", job.get("employer_name"))