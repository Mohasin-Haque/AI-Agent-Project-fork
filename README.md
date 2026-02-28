# Effortech Smart Portal  
### Developed by Irfan Ahamad

---

## 🚀 Overview

Effortech Smart Portal is an AI-powered issue resolution system designed to:

- Identify banking / Finacle-related issues
- Provide root cause analysis
- Display structured resolution steps
- Show step-wise reference images
- Display reference queries (read-only)
- Allow users to mark issue as resolved
- Escalate issue to CBS support team with ticket generation

Frontend is built using **React (Vite)** and connected to a **FastAPI backend** deployed on Render.

---

## 🌐 Live Deployment

**Frontend:**  
https://ai-agent-project-1-kq4v.onrender.com  

**Backend API:**  
https://ai-agent-project-he7a.onrender.com  

---

## 🏗 Tech Stack

### Frontend
- React (Vite)
- CSS
- Fetch API

### Backend
- FastAPI
- FAISS (Vector Search)
- OpenRouter Embeddings
- NumPy
- Render (Deployment)

---

## 📂 Project Structure

```
src/
│
├── components/
│   ├── QueryForm.jsx
│   ├── ResponseCard.jsx
│
├── api/
│   └── api.js
│
├── styles/
│   └── app.css
│
└── App.jsx
```

---

## 🔍 Features

### 1️⃣ Smart Issue Identification
- Embedding-based similarity search
- Matches user query with predefined bank issues

### 2️⃣ Detailed Resolution View
- Identified Issue
- Root Cause
- Step-by-step Resolution
- Step Images
- Reference Queries

### 3️⃣ Escalation System
- Generates CBS ticket ID
- Accepts user comments
- Displays escalation confirmation

### 4️⃣ Clean UI
- Structured layout
- Logo branding
- Responsive container
- Visual action buttons

---

## 📡 API Endpoints

### Query Endpoint

**POST** `/query`

Request:
```json
{
  "user_query": "Finacle login issue"
}
```

Response:
```json
{
  "issue_id": "CBS-101",
  "identified_issue": "1. Finacle Login Failure",
  "root_cause": "...",
  "resolution_steps": [],
  "step_assets": {},
  "reference_queries": {},
  "escalation_required": false
}
```

---

### Escalation Endpoint


  Note: the escalation endpoint now attempts to send an email with full details (reporter name, email, phone, search query, comments) to the configured escalation address. By default this POC sends to `airfan@effor.tech` unless you set `ESCALATION_TARGET_EMAIL`.

  Environment variables for email (optional, for live sending):

  ```
  SMTP_HOST=smtp.example.com
  SMTP_PORT=587
  SMTP_USER=you@example.com
  SMTP_PASS=your-smtp-password
  FROM_EMAIL=no-reply@example.com
  ESCALATION_TARGET_EMAIL=airfan@effor.tech
  ```

  If SMTP settings are not provided the backend will write the full email payload to `escalation_emails.log` for manual processing.
**POST** `/escalate`

> Frontend now sends the originating `system` field so the backend can route the ticket to the appropriate team.  
> - `Compass` / `Compass AML` → **AML team**  
> - `SDK` → **Digital team**  
> - all other systems (Finacle, NEFT, RTGS, etc.) default to **CBS**

Request:
```json
{
  "issue_id": "CBS-101",
  "user_comments": "Tried all steps",
  "system": "Compass AML"
}
```

Response:
```json
{
  "status": "ESCALATED",
  "ticket_id": "AML-54321",
  "message": "Issue escalated to AML support team"
}
```

---

## ⚙️ How It Works

1. User enters issue description.
2. Frontend calls `/query`.
3. Backend:
   - Generates embedding
   - Searches FAISS index
   - Returns best matched issue.
4. User can:
   - Mark issue as resolved
   - Escalate to CBS support

---

## 🔐 Environment Variables (Backend)

Set this in Render → Backend Service → Environment:

```
OPENAI_API_KEY=sk-or-xxxxxxxxxxxxxxxx
```

---

## 🧠 Core Logic

- Vector similarity search using FAISS
- Embedding model: `openai/text-embedding-3-small`
- Dynamic rendering of step images
- Dynamic rendering of reference queries
- Conditional UI states:
  - Resolved
  - Escalated
  - Pending

---

## 🎯 Future Enhancements

- ServiceNow Integration
- Email notifications
- Role-based authentication
- Admin dashboard
- Analytics tracking
- Persistent database storage

<h1 align=center> Project Admin ❤️ </h1>
<p align="center">

<table align="center">
    <tbody>
        <tr>
            <td align="center">
                <a href="https://github.com/Irfan-2002">
                    <img alt="" src="https://avatars.githubusercontent.com/Irfan-2002" width="100px;"><br>
                    <sub><b> Irfan Ahmad </b></sub>
                </a>
            </td>
        </tr>
    </tbody>
</table>

⭐ If you found this project useful, consider giving it a star!