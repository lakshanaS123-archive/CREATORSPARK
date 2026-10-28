# CreatorSpark 🚀

**Content Idea Generation & Planning Studio for Instagram Influencers & Social Media Creators**

CreatorSpark is a focused, polished, beginner-friendly web application designed to help social media creators brainstorm scroll-stopping hooks, structured outlines, captions, and hashtag strategies tailored to their exact niche and audience.

---

## 🌟 Current Status: Stage 2 Complete (Full Feature Implementation)

| Stage | Focus Area | Status |
| :--- | :--- | :--- |
| **Stage 1** | **Django Foundation & Project Architecture** | ✅ **Complete** |
| **Stage 2** | **Auth, Idea Generator, Saved Ideas, Planner, Studio, Audio & Media** | ✅ **Complete** |
| Stage 3 | Advanced Workflow Refinements & Analytics Enhancements | ⏳ Next |
| Stage 4 | Production Hardening, Security Audits & Deployment (Render / PostgreSQL) | ⏳ Planned |
| Stage 5 | Final Delivery & Polishing | ⏳ Planned |

---

## 🛠️ Technology Stack

- **Backend:** Python 3.13+, Django 6.1+
- **Frontend:** Django Templates, Semantic HTML5, CSS3 Custom Properties (Design System), Vanilla JavaScript (No heavy NPM/bundler dependencies)
- **Database:** SQLite for local development; PostgreSQL support via `dj-database-url` for production
- **Static Asset Pipeline:** WhiteNoise with automatic compression and caching
- **Media Uploads:** Managed via Django `MEDIA_ROOT` and Pillow with file size & type limits
- **WSGI Server:** Gunicorn (for Linux production environments such as Render)
- **Audio TTS:** Native browser Web Speech API (zero external audio API costs)

---

## 📐 Project Architecture

```text
CREATORSPARK/
├── build.sh                 # Cloud deployment script (Render / Linux PaaS)
├── manage.py                # Django management script
├── requirements.txt         # Minimal, strictly necessary dependencies
├── .env.example             # Template for local environment variables
├── .gitignore               # Excludes bytecode, SQLite, secrets, uploads
├── README.md                # Project documentation
│
├── creatorspark/            # Project configuration package
│   ├── __init__.py
│   ├── asgi.py              # ASGI configuration
│   ├── settings.py          # Environment-aware settings (SQLite/PostgreSQL)
│   ├── urls.py              # Root URL routing
│   └── wsgi.py              # WSGI configuration
│
├── core/                    # Core application
│   ├── __init__.py
│   ├── admin.py             # Admin registration for all models
│   ├── apps.py              # Core app configuration
│   ├── context_processors.py# Global metadata context processor
│   ├── models.py            # UserProfile, ContentIdea, PlannerEntry, ReferenceMedia
│   ├── tests.py             # Unit tests for views, health check, and isolation
│   ├── urls.py              # Core URL routing (landing, about, health, sample-api)
│   └── views.py             # Public landing, about, health, and rule preview logic
│
├── templates/               # Shared template hierarchy
│   ├── base.html            # Master layout with header, alerts, footer
│   ├── includes/
│   │   ├── navbar.html      # Responsive navigation & mobile drawer
│   │   ├── footer.html      # Footer with architecture & stage roadmap
│   │   └── messages.html    # Dismissible alert banners
│   └── core/
│       ├── landing.html     # Polished landing page & live generator preview
│       └── about.html       # Architecture, philosophy & stack overview
│
├── static/                  # Static assets
│   ├── css/
│   │   └── main.css         # Custom CSS design system & responsive layout
│   ├── js/
│   │   └── main.js          # Navigation toggle, alerts, live preview & TTS
│   └── img/
│       ├── logo.svg         # Brand SVG logo
│       └── favicon.svg      # SVG favicon
│
└── media/                   # User media directory (isolated from source)
    └── .gitkeep
```

---

## 🗄️ Data Models & User Isolation

Every private record in CreatorSpark is strictly isolated per authenticated user:

1. **`UserProfile`** — Linked 1-to-1 to Django's `User` model. Stores creator handle, primary niche, target audience, and bio notes.
2. **`ContentIdea`** — Stores generated or user-saved post ideas (title, hook, step outline, caption draft, hashtags, call-to-action, difficulty). Scoped to `user` via ForeignKey.
3. **`PlannerEntry`** — Schedule entries with planned dates, times, and status (`idea`, `planned`, `in_progress`, `ready`, `published`, `archived`). Scoped to `user`.
4. **`ReferenceMedia`** — Reference images and moodboards uploaded by creators. Scoped to `user` with strict 5MB size limit.

---

## 💡 Philosophy: Transparent Rule Engine First

- **Zero Paid API Fees:** CreatorSpark is completely usable without OpenAI, Anthropic, or Instagram Graph API credentials.
- **Predictable Quality:** Rule-based heuristics guarantee structured output: opening hooks, retention outlines, captions, and categorized hashtags.
- **Decoupled Architecture:** The generator service is modularly isolated. A real LLM provider (e.g. OpenAI or Google Gemini) can be connected in the future without altering data schemas.

---

## 🚀 Quickstart: Local Setup Instructions

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13.5)
- Git (optional for local tracking)

### 2. Set Up a Virtual Environment (Recommended)

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example file:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
*(By default, `.env` runs SQLite locally with `DEBUG=True`.)*

### 5. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run System Checks and Tests
```bash
# Django system check
python manage.py check

# Run automated test suite
python manage.py test
```

### 7. Create a Superuser (Optional for Django Admin)
```bash
python manage.py createsuperuser
```

### 8. Start the Local Server
```bash
python manage.py runserver
```

Open your browser and visit:
- **Landing Page:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health/](http://127.0.0.1:8000/health/)
- **About & Stack Page:** [http://127.0.0.1:8000/about/](http://127.0.0.1:8000/about/)
- **Admin Portal:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔒 Security & Deployment Readiness

- `DEBUG` is controlled by the environment variable `DEBUG` (defaults to `True` for local dev, must be `False` in production).
- Database dynamically switches from SQLite to PostgreSQL when `DATABASE_URL` is provided.
- `SECRET_KEY` / `DJANGO_SECRET_KEY`: Production fails immediately with `ImproperlyConfigured` if an explicit production key is missing when `DEBUG=False`.
- Automatic Render detection: `RENDER_EXTERNAL_HOSTNAME` is detected and automatically added to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
- WhiteNoise is configured for static caching, gzip, and brotli compression.
- CSRF protection is enabled across all routes.
- Security headers (SSL redirect, HSTS, XSS protection, Frame options) activate automatically when `DEBUG=False`.

---

## ☁️ Render Deployment Guide

When you are ready to deploy to Render:

### 1. Create a PostgreSQL Database on Render
1. Create a **New PostgreSQL** database on Render (e.g. `creatorspark-db`).
2. Copy the **Internal Database URL** (or External Database URL).

### 2. Create a Web Service on Render
1. Create a **New Web Service** and connect your GitHub repository.
2. Configure the service settings:
   - **Environment:** `Python`
   - **Root Directory:** (leave blank for repository root)
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn creatorspark.wsgi:application`
3. Add **Environment Variables** in the Render Dashboard:
   - `DEBUG`: `False`
   - `SECRET_KEY`: (Generate a secure 50+ character random secret string)
   - `DATABASE_URL`: (Paste the PostgreSQL connection URL from Step 1)
   - `SECURE_SSL_REDIRECT`: `True`
4. Deploy the service!

> [!NOTE]
> **Ephemeral Storage Notice:** On Render's free tier, the container filesystem is ephemeral. Uploaded reference media in `/media/` will reset upon redeployments unless a persistent disk or cloud storage provider (e.g., AWS S3 or Cloudinary) is attached.

---

## 🐙 Git Commands to Publish

When you are ready to push your repository to GitHub:

```bash
# 1. Initialize git (if not already initialized)
git init

# 2. Add all files (respecting .gitignore)
git add .

# 3. Commit the project
git commit -m "Complete CreatorSpark Instagram Idea & Planning Platform"

# 4. Link your remote repository and push
git remote add origin https://github.com/YOUR_USERNAME/CREATORSPARK.git
git branch -M main
git push -u origin main
```

