# Pathfinder – Career & Skill Roadmap Generator

Pathfinder is a full-stack, rule-based career planning web application for students. It compares a student's self-assessed skills against explicit career requirements, classifies each skill as **Matched**, **Partial**, or **Missing**, calculates a weighted readiness percentage, and generates an ordered roadmap with resources and mini-projects.

## Stack

- **Frontend:** HTML5, CSS3, Bootstrap 5, vanilla JavaScript, Chart.js
- **Backend:** Python Flask, Blueprints, REST APIs, Jinja templates
- **Database:** SQLite + SQLAlchemy ORM; MySQL-ready through `DATABASE_URL`
- **Authentication:** Flask-Login + Werkzeug password hashing
- **CSRF:** Flask-WTF CSRFProtect; AJAX requests send the CSRF token header
- **Testing:** pytest

## Project structure

```text
pathfinder/
├── app/
│   ├── __init__.py
│   ├── engine.py
│   ├── models.py
│   ├── blueprints/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── api.py
│   │   └── admin.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── onboarding.html
│   │   ├── careers.html
│   │   ├── gap.html
│   │   ├── roadmap.html
│   │   ├── dashboard.html
│   │   ├── compare.html
│   │   ├── admin.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── app.js
│           ├── onboarding.js
│           ├── careers.js
│           ├── gap.js
│           ├── roadmap.js
│           ├── dashboard.js
│           ├── compare.js
│           └── admin.js
├── tests/test_engine.py
├── config.py
├── requirements.txt
├── .env.example
├── run.py
├── seed.py
└── README.md
```

## Database schema

```text
users
  id PK
  email UNIQUE
  password_hash
  role
  created_at
      │
      ├────────── profiles.user_id
      ├────────── user_skills.user_id ───── skills.id
      └────────── roadmaps.user_id
                                      │
careers.id ───── career_skills.career_id
skills.id   ─── career_skills.skill_id
careers.id ───── roadmaps.career_id
roadmaps.id ──── roadmap_steps.roadmap_id
skills.id   ─── roadmap_steps.skill_id
resources.id ─── roadmap_steps.resource_id
```

Tables implemented: `users`, `profiles`, `careers`, `skills`, `career_skills`, `user_skills`, `roadmaps`, `roadmap_steps`, `resources`.

## Quick start

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment (optional but recommended)

Copy `.env.example` to `.env` and change the secret key.

For SQLite:

```env
SECRET_KEY=replace-with-a-long-random-value
DATABASE_URL=sqlite:///pathfinder.db
```

For MySQL, install `PyMySQL` (already in requirements) and set:

```env
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/pathfinder
```

### 4. Seed the database

```bash
python seed.py
```

The seed script is idempotent: running it again adds missing records without duplicating existing career/skill mappings.

Seeded content includes **8 career paths**, 50+ skills, career requirements, and learning resources.

### 5. Run Flask

Either:

```bash
flask --app run.py run --debug
```

or:

```bash
python run.py
```

Open: `http://127.0.0.1:5000`

## Demo admin

- Email: `admin@pathfinder.local`
- Password: `Admin@123`
- Admin UI: `http://127.0.0.1:5000/admin-ui`

Change this credential before deploying publicly.

## REST API

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Profile and skills

- `GET /api/profile`
- `PUT /api/profile`
- `POST /api/profile/skills`
- `GET /api/skills`

### Careers

- `GET /api/careers?q=&category=`
- `GET /api/careers/<career_id>`
- `GET /api/careers/<career_id>/skills`

### Gap analysis

- `POST /api/gap-analysis`

Example:

```json
{"career_id": 1}
```

### Roadmaps

- `POST /api/roadmaps/generate`
- `GET /api/roadmaps`
- `GET /api/roadmaps/<roadmap_id>`
- `PATCH /api/roadmaps/steps/<step_id>`

Example PATCH body:

```json
{"status":"Completed"}
```

### Career comparison

- `GET /api/compare?career_a=1&career_b=2`

### Admin

- `GET/POST /admin/careers`
- `PUT/DELETE /admin/careers/<id>`
- `GET/POST /admin/skills`
- `PUT/DELETE /admin/skills/<id>`
- `GET/POST /admin/career-skills/<career_id>` / `/admin/career-skills`
- `PUT/DELETE /admin/career-skills/<link_id>`

All state-changing requests are protected by Flask-WTF CSRF.

## Rule-based gap engine

Each career skill has a required level:

- Beginner = 1
- Intermediate = 2
- Advanced = 3

The engine compares required level with the student's current level:

```text
current >= required       → Matched
0 < current < required    → Partial
current == 0              → Missing
```

Readiness is a weighted percentage. High-priority skills receive weight 3, Medium weight 2, and Low weight 1.

```text
Readiness = weighted achieved level / weighted required level × 100
```

## Security notes

- Passwords are never stored in plain text; Werkzeug's password hashing is used.
- SQLAlchemy parameterization/ORM access is used instead of string-built SQL queries.
- Jinja escapes template output; dynamic JavaScript uses an `escapeHtml` helper before injecting database values into HTML.
- Flask-WTF CSRF protection is enabled globally.
- Session cookies are HTTP-only and SameSite=Lax.
- For production, use HTTPS, a strong random `SECRET_KEY`, secure cookies, rate limiting, audit logs, and a managed database.

## Tests

```bash
pytest
```

The included tests cover classification and weighted readiness calculations in the gap engine.

## UI/UX

The interface is mobile-first and includes:

- Indigo / sky / amber / green / navy design palette
- Poppins headings + Lato body text
- Rounded cards and soft shadows
- Responsive Bootstrap layout
- Gradient primary actions
- Hover transitions
- Skeleton loading state
- Toast notifications
- Dark mode with local persistence
- Semantic labels and keyboard-friendly controls
- Empty, 404, and 500 states
- Career search/filter
- Timeline roadmap
- Chart.js radar and doughnut charts

## Future enhancements

1. Resume Builder
2. Job Recommendations
3. Interview Preparation
4. Multi-language support
5. Mobile application
6. AI-assisted resource recommendations as a separate intelligence layer
7. Email reminders and weekly progress reports
8. More detailed prerequisite graphs
9. Admin audit logs and bulk import/export
10. Production deployment configuration for Render, Railway, Docker, or AWS
