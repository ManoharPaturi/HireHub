# HireHub Backend

FastAPI + SQLAlchemy backend. **MySQL only** — there is no SQLite fallback.

## Requirements

- Python 3.10+
- MySQL 8.0 (running locally or remotely)

## Setup

### 1. Create the database

```sql
CREATE DATABASE internship_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

> Use `utf8mb4_0900_ai_ci` (the MySQL 8 default). Other collations can trigger
> `Error 3780` on foreign-key creation.

### 2. Configure credentials

Edit `app/core/config.py` (or set environment variables):

```bash
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DB=internship_portal
```

### 3. Install & run

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

On first startup, SQLAlchemy creates all tables automatically and seeds demo data:

**Demo accounts** (password shown for each):

| Role      | Email                   | Password       |
|-----------|-------------------------|----------------|
| Student   | student@demo.com        | password123    |
| Recruiter | recruiter@stripe.com    | recruiter123   |
| Recruiter | recruiter@notion.com    | recruiter123   |
| Recruiter | recruiter@figma.com     | recruiter123   |
| Recruiter | recruiter@spotify.com   | recruiter123   |
| Recruiter | recruiter@vercel.com    | recruiter123   |
| Recruiter | recruiter@linear.com    | recruiter123   |

Every seeded internship is linked to its company's recruiter.

## API docs

Interactive docs: `http://127.0.0.1:8000/docs`

## Notes

- Uploaded documents (resumes, cover letters) are stored **base64-encoded in the
  `documents.file_data` column** (`MEDIUMTEXT`, 8 MB cap). No filesystem storage.
- Gender-aware avatars are auto-assigned on student registration from a curated
  Unsplash pool via `app/core/avatars.py`.
