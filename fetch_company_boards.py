import requests
from enrich_direct_links import slugify, check_greenhouse, check_lever, check_ashby, check_workable

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Nvidia",
    "Salesforce", "Adobe", "Oracle", "IBM", "Intel", "Cisco", "Qualcomm",
    "SAP America", "Tata Consultancy Services", "Infosys", "Wipro",
    "Cognizant", "Capgemini America", "Accenture", "Deloitte Consulting",
    "HCL America", "Tech Mahindra", "Mindtree", "L&T Infotech", "Mphasis",
    "Larsen & Toubro Infotech", "Syntel", "iGate", "UST Global", "Virtusa",
    "Hexaware Technologies", "Sonata Software", "Persistent Systems",
    "JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Bank of America",
    "Citigroup", "Wells Fargo", "American Express", "Capital One",
    "Visa Inc.", "Mastercard", "PayPal", "Charles Schwab",
    "Fidelity Investments", "BlackRock", "State Street Corporation",
    "Pfizer", "Johnson & Johnson", "Merck & Co.", "UnitedHealth Group",
    "Cigna", "Eli Lilly", "Amgen", "Gilead Sciences", "Bristol Myers Squibb",
    "Cerner", "ServiceNow", "Workday", "Snowflake", "Splunk",
    "Palantir Technologies", "Atlassian", "VMware", "Dell Technologies",
    "HP Inc.", "Hewlett Packard Enterprise", "Juniper Networks",
    "Akamai Technologies", "Twilio", "MongoDB", "Databricks", "Tesla",
    "Ford Motor Company", "General Motors", "Boeing", "Lockheed Martin",
    "Honeywell", "General Electric", "Walmart Global Tech",
    "Target Corporation", "Best Buy", "Home Depot", "Costco Wholesale",
    "eBay", "AT&T", "Verizon", "T-Mobile USA", "Comcast", "Anthropic",
    "OpenAI", "Scale AI", "Together AI", "Hugging Face", "Perplexity AI",
    "Anyscale", "Glean", "Uber", "Lyft", "Airbnb", "DoorDash", "Instacart", "Pinterest", "Snap Inc.",
    "Reddit", "LinkedIn", "Zoom", "Dropbox", "Box Inc.", "DocuSign", "HubSpot",
    "Intuit", "Autodesk", "Adobe Systems", "Synopsys", "Cadence Design Systems",
    "Citrix Systems", "AMD", "Broadcom", "Texas Instruments", "Micron Technology",
    "Applied Materials", "Lam Research", "KLA Corporation", "Western Digital",
    "Seagate Technology", "Analog Devices", "EY", "PwC", "KPMG", "McKinsey & Company",
    "Boston Consulting Group", "Booz Allen Hamilton", "Slalom Consulting",
    "West Monroe Partners", "ICF International", "Genpact", "NTT DATA",
    "DXC Technology", "Unisys", "CGI Group", "Atos North America", "MetLife",
    "Prudential Financial", "Allstate", "Travelers Companies",
    "Liberty Mutual Insurance", "Aetna", "Humana", "AbbVie", "Biogen",
    "Regeneron Pharmaceuticals", "Moderna", "Vertex Pharmaceuticals", "Illumina",
    "Thermo Fisher Scientific", "Becton Dickinson", "Stryker Corporation",
    "Medtronic", "Charter Communications", "Disney", "Warner Bros. Discovery",
    "Paramount Global", "Sony Electronics", "Electronic Arts",
    "Northrop Grumman", "Raytheon Technologies", "L3Harris Technologies",
    "General Dynamics", "SpaceX", "Collins Aerospace", "Chevron", "ExxonMobil",
    "Schlumberger", "Halliburton", "Caterpillar", "Emerson Electric", "FedEx",
    "UPS", "C.H. Robinson", "Flexport", "XPO Logistics", "Cohere", "Mistral AI",
    "Stability AI", "Replit", "Vercel", "Cresta", "Sierra", "Harvey AI",
    "Runway ML", "Character.AI", "Adept AI", "Inflection AI", "Weights & Biases",
    "Pinecone", "Nike", "Starbucks", "PepsiCo", "Coca-Cola Company",
    "Procter & Gamble", "Unilever US", "Colgate-Palmolive", "Kimberly-Clark",
    "Mondelez International", "General Mills", "Kraft Heinz", "Estée Lauder",
    "L'Oréal USA", "Albertsons", "Kroger", "U.S. Bank", "PNC Financial Services",
    "Truist Financial", "Ally Financial", "Synchrony Financial",
    "Discover Financial Services", "Stripe", "Square", "Plaid", "Robinhood",
    "Coinbase", "Affirm", "Chime", "SoFi Technologies", "Brex", "Anthem",
    "Centene Corporation", "Molina Healthcare", "Epic Systems", "Athenahealth",
    "Teladoc Health", "GE Healthcare", "Philips North America",
    "Siemens Healthineers", "Veeva Systems", "Rivian", "Lucid Motors",
    "Toyota Motor North America", "Honda North America", "Nissan North America",
    "Volkswagen Group of America", "BMW of North America", "Stellantis",
    "CrowdStrike", "Palo Alto Networks", "Fortinet", "Zscaler", "Okta",
    "SailPoint", "Tenable", "Rapid7", "Proofpoint", "CyberArk", "Cloudera",
    "Teradata", "SAS Institute", "Informatica", "Alteryx", "Domo", "Sisense",
    "ThoughtSpot", "Looker", "Tableau", "Activision Blizzard",
    "Take-Two Interactive", "Riot Games", "Epic Games", "Roblox Corporation",
    "Unity Technologies", "Zynga", "Zillow Group", "Redfin", "CBRE Group",
    "JLL", "Opendoor", "Compass Inc.", "CoStar Group", "Chegg", "Coursera",
    "2U Inc.", "Pearson North America", "Duolingo", "Khan Academy",
    "Expedia Group", "Booking Holdings", "Marriott International",
    "Hilton Worldwide", "Delta Air Lines", "United Airlines", "Figma",
    "Notion Labs", "Canva", "Ramp", "Rippling", "Deel", "Bloomberg LP", "Cypress Semiconductor", "Broad Institute of MIT and Harvard", "Battelle Memorial Institute",
    "Allen Institute for AI", "Mayo Clinic", "Fred Hutchinson Cancer Research Center",
    "Cleveland Clinic Foundation", "Dana-Farber Cancer Institute",
    "Memorial Sloan Kettering Cancer Center", "St. Jude Children's Research Hospital",
    "The Scripps Research Institute", "Children's Hospital of Philadelphia",
    "Sanford Burnham Prebys Medical Discovery Institute",
    "The Salk Institute for Biological Studies",
    "Whitehead Institute for Biomedical Research",
    "Woods Hole Oceanographic Institution", "Icahn School of Medicine at Mount Sinai",
    "Indiana University Health Care Associates Inc.", "Brookings Institution",
    "Guttmacher Institute", "RAND Corporation", "Stanford University",
    "University of Michigan", "MIT", "Carnegie Mellon University", "University of Washington", "UC Berkeley", "Georgia Tech",
    "University of Illinois Urbana-Champaign", "Caltech", "Chan Zuckerberg Initiative",
]

ROLE_KEYWORDS = [
    "ai", "machine learning", "ml engineer", "llm", "generative ai",
    "nlp", "rag", "applied ai", "ai platform", "ai infrastructure",
    "ai systems",
]


def is_relevant(title):
    title_lower = title.lower()
    return any(kw in title_lower for kw in ROLE_KEYWORDS)


def fetch_greenhouse_jobs(slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []
        return [
            {
                "job_title": j.get("title"),
                "employer_name": slug,
                "best_apply_link": j.get("absolute_url"),
                "best_apply_source": "Greenhouse (direct)",
                "job_description": "",
                "job_posted_at_timestamp": None,
            }
            for j in resp.json().get("jobs", []) if is_relevant(j.get("title", ""))
        ]
    except requests.RequestException:
        return []


def fetch_lever_jobs(slug):
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []
        return [
            {
                "job_title": j.get("text"),
                "employer_name": slug,
                "best_apply_link": j.get("hostedUrl"),
                "best_apply_source": "Lever (direct)",
                "job_description": "",
                "job_posted_at_timestamp": None,
            }
            for j in resp.json() if is_relevant(j.get("text", ""))
        ]
    except requests.RequestException:
        return []


def fetch_ashby_jobs(slug):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []
        return [
            {
                "job_title": j.get("title"),
                "employer_name": slug,
                "best_apply_link": j.get("jobUrl"),
                "best_apply_source": "Ashby (direct)",
                "job_description": "",
                "job_posted_at_timestamp": None,
            }
            for j in resp.json().get("jobs", []) if is_relevant(j.get("title", ""))
        ]
    except requests.RequestException:
        return []


def fetch_workable_jobs(slug):
    url = f"https://apply.workable.com/api/v1/widget/accounts/{slug}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []
        jobs = []
        for j in resp.json().get("jobs", []):
            title = j.get("title", "")
            if is_relevant(title):
                shortcode = j.get("shortcode")
                jobs.append({
                    "job_title": title,
                    "employer_name": slug,
                    "best_apply_link": f"https://apply.workable.com/{slug}/j/{shortcode}/",
                    "best_apply_source": "Workable (direct)",
                    "job_description": "",
                    "job_posted_at_timestamp": None,
                })
        return jobs
    except requests.RequestException:
        return []


def fetch_smartrecruiters_jobs(slug):
    url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []
        jobs = []
        for j in resp.json().get("content", []):
            title = j.get("name", "")
            if is_relevant(title):
                jobs.append({
                    "job_title": title,
                    "employer_name": slug,
                    "best_apply_link": j.get("ref"),
                    "best_apply_source": "SmartRecruiters (direct)",
                    "job_description": "",
                    "job_posted_at_timestamp": None,
                })
        return jobs
    except requests.RequestException:
        return []


def fetch_bamboohr_jobs(slug):
    url = f"https://{slug}.bamboohr.com/jobs/embed2.php?version=1"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return []
        jobs = []
        for j in resp.json():
            title = j.get("title", "")
            if is_relevant(title):
                jobs.append({
                    "job_title": title,
                    "employer_name": slug,
                    "best_apply_link": f"https://{slug}.bamboohr.com/careers/{j.get('id')}",
                    "best_apply_source": "BambooHR (direct)",
                    "job_description": "",
                    "job_posted_at_timestamp": None,
                })
        return jobs
    except (requests.RequestException, ValueError):
        return []


def fetch_all_company_boards():
    """Check all target companies across all 6 ATS platforms, return relevant jobs only."""
    all_jobs = []
    fetch_functions = [
        fetch_greenhouse_jobs,
        fetch_lever_jobs,
        fetch_ashby_jobs,
        fetch_workable_jobs,
        fetch_smartrecruiters_jobs,
        fetch_bamboohr_jobs,
    ]

    for company in COMPANIES:
        slug = slugify(company)
        for fetch_fn in fetch_functions:
            jobs = fetch_fn(slug)
            if jobs:
                platform_name = fetch_fn.__name__.replace("fetch_", "").replace("_jobs", "")
                print(f"  → Found {len(jobs)} relevant jobs at {company} ({platform_name})")
            all_jobs.extend(jobs)
    return all_jobs


if __name__ == "__main__":
    print(f"Checking {len(COMPANIES)} companies across 6 ATS platforms...\n")
    jobs = fetch_all_company_boards()
    print(f"\nTotal relevant jobs found: {len(jobs)}\n")
    for job in jobs[:10]:
        print(f"{job['job_title']} - {job['employer_name']} ({job['best_apply_source']})")
        print(job['best_apply_link'])
        print("---")