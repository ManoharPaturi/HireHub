# HireHub — Entity Relationship Diagram (v2, complete)

Complete data model for the Internship Portal — **student module + host/employer (recruiter) module + admin role**. This is the corrected, full-attribute version of the earlier diagram.

> **About "hosts":** the portal implements the *host organization* (the company that hosts interns) as **`recruiter_profiles`** — a 1:1 profile linked to a `users` account with `role = "recruiter"`. The host side of the diagram is: `users → recruiter_profiles → internships / interviews`.

## Files

| File | Description |
|------|-------------|
| **`er-diagram-v2.png`** | ⭐ Rendered high-resolution PNG (ready to paste into reports/slides). |
| **`er-diagram-v2.drawio`** | ⭐ Editable draw.io / diagrams.net source — 12 tables with full attribute rows, crow's-foot connectors, color-coded domains. |
| **`er-diagram.mmd`** | Mermaid source — renders natively on GitHub, VS Code, GitLab, Notion. |
| **`er-diagram.html`** | Self-contained interactive HTML render (bundled `mermaid.min.js`, no internet needed). |
| **`../backend/schema.sql`** | The equivalent MySQL `CREATE TABLE` DDL. |

> Schema source of truth: [`backend/app/db/models.py`](../backend/app/db/models.py) (SQLAlchemy ORM). MySQL in production.

## Schema overview — 12 tables

### Core identity
- **`users`** — central auth identity. `email` (unique), `password_hash`, `role` (`student` | `recruiter` (host) | `admin`).
  - 1:1 → `students`, 1:1 → `recruiter_profiles`
  - 1:N → `notifications`, 1:N → `messages` (as sender & receiver)

### Host / employer domain (the "host" side)
- **`recruiter_profiles`** — the **host organization** & its contact person: company name/logo/website/size, industry, designation, phone, LinkedIn, location. 1:1 with `users`.
- **`internships`** — roles posted **by the host**. N:1 → `recruiter_profiles` (nullable so admin/external posts work). Carries stipend (+currency), mode, duration, deadline, skills, external-link flags.
- **`interviews`** — interviews the host conducts. N:1 → `recruiter_profiles`, `applications`, `internships` (SET NULL).

### Student domain
- **`students`** — profile (university, degree, CGPA, gender, avatar, preferred mode, portfolio, etc.). 1:1 with `users`.
- **`documents`** — uploaded files (resume, transcripts) incl. base64 `file_data`, `content_type`, `file_size`. N:1 → `students`.
- **`skills`** — global skill catalog. `name` unique.
- **`student_skills`** — join table (M:N `students` ↔ `skills`) with `proficiency_level`.
- **`applications`** — a student applying to an internship. `status` lifecycle: `Applied → Under Review → Shortlisted → Interview Scheduled → Accepted/Rejected`. `resume_url` holds an external URL **or** a base64 data-URI upload (MEDIUMTEXT).
- **`saved_internships`** — bookmarked roles (M:N `students` ↔ `internships`).

### Communication
- **`notifications`** — per-user alerts. N:1 → `users`.
- **`messages`** — direct messages between any two users. **Two FKs to `users`** (`sender_id`, `receiver_id`).

## All 16 relationships

| From | Cardinality | To | Meaning |
|------|-------------|----|---------|
| users | 1 : 0..1 | recruiter_profiles | is host account |
| users | 1 : 0..1 | students | is student account |
| users | 1 : N | notifications | receives |
| users | 1 : N | messages | sends (as sender) |
| users | 1 : N | messages | receives (as receiver) |
| recruiter_profiles | 1 : N | internships | hosts / posts |
| recruiter_profiles | 1 : N | interviews | conducts |
| students | 1 : N | documents | uploads |
| students | 1 : N | student_skills | has |
| skills | 1 : N | student_skills | tagged in |
| students | 1 : N | applications | submits |
| internships | 1 : N | applications | receives |
| students | 1 : N | saved_internships | bookmarks |
| internships | 1 : N | saved_internships | saved in |
| internships | 0..1 : N | interviews | for (SET NULL) |
| applications | 1 : N | interviews | leads to |

## Key constraints & cascades

- All foreign keys use `ON DELETE CASCADE` except `interviews.internship_id` which uses `SET NULL` (an interview survives if the post is removed).
- `users.email`, `skills.name` are `UNIQUE`.
- `students.user_id` and `recruiter_profiles.user_id` are `UNIQUE` (enforces the 1:1).
- `internships.recruiter_id` is nullable (admin/external postings).
- `applications.resume_url` and `documents.file_data` are `MEDIUMTEXT` (base64 uploads — a VARCHAR silently fails on real files).
- Indexed: email, skill names, internship title/company/location, and all FKs.

## Corrections vs. the previous hand-drawn diagram (Drawing 43)

1. **Host side made explicit** — `recruiter_profiles` labelled as the host organization; `users 1:1 recruiter_profiles` labelled "is host account"; internships marked "hosts / posts".
2. **`messages` fixed** — it is user↔user via `sender_id` + `receiver_id` (both → `users.id`), not a single `recruiter_id`.
3. **Removed dangling `documents → applications` link** — documents belong to `students` only; a resume attached to an application lives in `applications.resume_url`.
4. **`saved_internships` re-anchored to `students`** (not `users`).
5. **Added missing attributes** — `students.gender`, `documents.content_type / file_size / file_data`, `internships.stipend_currency / is_external / external_link`, `applications.recruiter_notes`, `users.role` now includes `admin`.
6. **Crow's-foot cardinalities drawn on every edge**, including the optional one (`|o--`) on `internships → interviews` for the SET NULL FK.

## Regenerating the PNG

The PNG was captured from `er-diagram.html`. To regenerate at another resolution, serve the `docs/` folder and screenshot it, or:

```bash
# requires @mermaid-js/mermaid-cli (downloads its own Chromium)
npx -p @mermaid-js/mermaid-cli mmdc -i docs/er-diagram.mmd -o docs/er-diagram.png -w 2400 -H 1600 -b transparent
```
