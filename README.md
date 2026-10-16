# HireHub - Internship Portal

A DBMS academic project that connects students, recruiters, and administrators through a shared internship recruitment workflow.

## Features

- **Students:** academic profiles, skills, document uploads, internship search and filters, bookmarks, applications, and status tracking.
- **Recruiters:** internship posting and management, candidate profiles and resumes, table/Kanban applicant views, status updates, and interview scheduling.
- **Communication:** application-connected student/recruiter messaging and stored notifications with unread counts.
- **Administration:** account and posting management, application oversight, summary statistics, and grouped reports.
- **Recommendations:** database rules match student skills or preferred work mode and order results by stipend. This is not a trained AI recommendation model.

## Stack

| Layer | Technology |
| --- | --- |
| Interface | React, TypeScript, Tailwind CSS, Vite |
| API | FastAPI, Pydantic |
| Database access | SQLAlchemy, PyMySQL |
| Database | MySQL 8 |
| Review presentation | LaTeX Beamer |

## Run locally

Use Python 3.10 or later, a Node.js version compatible with the frontend's Vite dependency, and a running MySQL 8 server.

### 1. Create the database

```sql
CREATE DATABASE internship_portal
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

### 2. Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set the database password and a random JWT secret in `backend/.env`. Then run:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The backend creates missing tables and seeds demonstration accounts and records at startup. API documentation is available at <http://127.0.0.1:8000/docs>.

### 3. Start the frontend

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite. The API client currently points to `http://127.0.0.1:8000/api`.

### Demo accounts

These are intentional sample credentials created by the initialization script, not production credentials.

| Role | Email | Password |
| --- | --- | --- |
| Student | student@demo.com | password123 |
| Recruiter | recruiter@stripe.com | recruiter123 |
| Administrator | admin@hirehub.com | admin123 |

Other sample recruiter accounts are documented in [backend/README.md](backend/README.md). Administrators use the separate `/admin` entry point.

## Database and review presentation

- [SQLAlchemy models](backend/app/db/models.py): application schema source of truth, with 12 tables and 16 foreign-key relationships.
- [SQL reference](backend/schema.sql): an earlier SQL schema snapshot. It does not contain every field in the current models.
- [Eight-slide Beamer source](output/beamer/HireHub_DBMS_Review.tex) and [compiled presentation](output/beamer/HireHub_DBMS_Review.pdf).
- [Offline ER and UML viewer](output/diagrams/index.html), with [SVG/PNG images and editable definitions](output/diagrams/README.md).

## Compile the review presentation

Open `output/beamer/HireHub_DBMS_Review.tex` in Overleaf or a local LaTeX editor and compile with pdfLaTeX. It is a standalone Beamer document with hidden speaker notes. It contains exactly eight slides for a five-minute review.

## Project status and limitations

This repository is an academic demonstration. The interview list and scheduling are implemented; the calendar grid and several recruiter settings remain placeholders. Email password-reset delivery is not implemented. Messaging and notifications refresh through polling. Resumes use Base64 text storage in MySQL, with an 8 MiB upload limit.

The landing page includes hard-coded promotional figures, which are not measured results. Demonstration company names and profiles are sample data and do not imply partnerships. Placement impact and large-scale performance have not been measured.

Production use would require stronger password handling, access-control hardening, database constraints and migrations, and deployment configuration. Local secrets belong in ignored environment files.

## Project team

| Name | Roll number |
| --- | --- |
| Manohar Paturi | CB.SC.U4AIE24339 |
| Sainath B | CB.SC.U4AIE24309 |
| Pushpak K | CB.SC.U4AIE24328 |
| Shanmukh Badam | CB.SC.U4AIE24307 |
