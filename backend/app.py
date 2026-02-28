import json
import os
import smtplib
from email.message import EmailMessage
import faiss
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------
# Load Environment Variables
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------------
# OpenRouter Client
# -----------------------------
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://ai-agent-project-1-kq4v.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load Issues
# -----------------------------
with open("bank_issues.json", "r", encoding="utf-8") as f:
    issues = json.load(f)

# -----------------------------
# Prepare Texts for Embedding
# (No numbering here – keep embeddings clean)
# -----------------------------
texts = []
for issue in issues:
    titles = issue.get("issue_titles") or [issue.get("issue_title", "")]
    titles = [t.strip() for t in titles if t.strip()]
    symptoms = issue.get("symptoms", [])
    texts.append(f"{' '.join(titles)} {' '.join(symptoms)}")

# -----------------------------
# Build Embeddings (ONCE)
# -----------------------------
embeddings = []
for text in texts:
    embedding = client.embeddings.create(
        model="openai/text-embedding-3-small",
        input=text
    ).data[0].embedding
    embeddings.append(embedding)

dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

# -----------------------------
# Request Models
# -----------------------------
class QueryRequest(BaseModel):
    user_query: str


class EscalationRequest(BaseModel):
    issue_id: str
    user_comments: str | None = None
    system: str | None = None
    reporter_name: str | None = None
    reporter_email: str | None = None
    reporter_phone: str | None = None
    search_query: str | None = None

# -----------------------------
# Query API
# -----------------------------
@app.post("/query")
def query_issue(req: QueryRequest):
    query_embedding = client.embeddings.create(
        model="openai/text-embedding-3-small",
        input=req.user_query
    ).data[0].embedding

    _, indexes = index.search(
        np.array([query_embedding]).astype("float32"), 1
    )

    issue = issues[indexes[0][0]]

    raw_titles = issue.get("issue_titles") or [issue.get("issue_title", "")]
    raw_titles = [t.strip() for t in raw_titles if t.strip()]

    # ✅ Numbered & newline-separated titles
    identified_issue = "\n".join(
        f"{i + 1}. {title}"
        for i, title in enumerate(raw_titles)
    )

    return {
        "issue_id": issue.get("issue_id"),
        "system": issue.get("system"),
        "identified_issue": identified_issue,
        "root_cause": issue.get("root_cause", ""),
        "resolution_steps": issue.get("resolution_steps", []),
        "step_assets": issue.get("step_assets", {}),
        "reference_queries": issue.get("reference_queries", {}),
        "escalation_required": issue.get("escalation", False)
    }

# -----------------------------
# Escalation API
# -----------------------------
@app.post("/escalate")
def escalate_issue(req: EscalationRequest):
    """
    POC escalation handler
    Future:
    - ServiceNow / Remedy
    - Email
    - team-specific ticketing
    """

    # determine support team from the provided system string
    team = "CBS"
    if req.system:
        s = req.system.lower()
        if "compass" in s or "aml" in s:
            team = "AML"
        elif "sdk" in s:
            team = "Digital"

    ticket_id = f"{team}-{np.random.randint(10000, 99999)}"
    message = f"Issue escalated to {team} support team"

    # build email content with all details
    body_lines = [
        f"Ticket ID: {ticket_id}",
        f"Target Team: {team}",
        "",
        "Reporter details:",
        f"  Name: {req.reporter_name}",
        f"  Email: {req.reporter_email}",
        f"  Phone: {req.reporter_phone}",
        "",
        "Escalation details:",
        f"  Issue ID: {req.issue_id}",
        f"  System: {req.system}",
        f"  Search Query: {req.search_query}",
        f"  User Comments: {req.user_comments}",
        "",
        "Please see the matched issue and resolution steps in the portal."
    ]
    body = "\n".join(str(l) for l in body_lines)

    email_sent = False

    # POC: send email to configured target or fallback address
    to_address = os.getenv("ESCALATION_TARGET_EMAIL", "airfan@effor.tech")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    from_addr = os.getenv("FROM_EMAIL", smtp_user or f"no-reply@{os.getenv('HOSTNAME','local')}")

    if smtp_host and smtp_port and smtp_user and smtp_pass:
        try:
            msg = EmailMessage()
            msg["Subject"] = f"Escalation: {req.issue_id} -> {team} ({ticket_id})"
            msg["From"] = from_addr
            msg["To"] = to_address
            msg.set_content(body)

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            email_sent = True
        except Exception as e:
            # fallback: write to a local log file for inspection
            with open("escalation_email_errors.log", "a", encoding="utf-8") as fh:
                fh.write(f"{ticket_id} - email send failed: {e}\n")
                fh.write(body + "\n\n")
            email_sent = False
    else:
        # SMTP not configured: save to local file for manual processing
        with open("escalation_emails.log", "a", encoding="utf-8") as fh:
            fh.write(f"{ticket_id} - SMTP not configured, saving payload:\n")
            fh.write(body + "\n\n")

    return {
        "status": "ESCALATED",
        "ticket_id": ticket_id,
        "message": message,
        "email_sent": email_sent,
        "target_team": team
    }