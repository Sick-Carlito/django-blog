# Django Blog — Portfolio Project

A full-featured blog platform built with **Django**. This project is a learning and portfolio project focused on building a secure, deployable, SEO-friendly blog that can be monetized with ads and affiliates and showcased to clients or employers.

## Project Goals
1. Build a production-ready blog platform with Django that includes:
   - Post creation, editing, and management (multi-author support).
   - Categories, tags, comments, and admin management.
   - SEO best-practices: friendly slugs, sitemaps, meta tags, OpenGraph.
   - Responsive, accessible frontend (mobile-first).
2. Learn and document a complete web app workflow:
   - Local development with virtualenv and environment variables.
   - Testing (TDD), migrations, and database setup.
   - Deployment to a hosting provider with HTTPS, static/media handling.
3. Portfolio & Documentation:
   - Maintain clear documentation and a case study showing architecture, deployment, and SEO results.

## Quick Start (local development)
```bash
# Clone repo (or if you already have it locally skip cloning)
git clone https://github.com/your-username/django-blog.git
cd django-blog

# Create & activate venv (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate

# Or Windows PowerShell:
# py -3 -m venv .venv
# .\.venv\Scripts\Activate.ps1

# Install requirements
python -m pip install -r requirements.txt

# Copy example env and edit .env with your values
cp .env.example .env
# Edit .env to add SECRET_KEY, DEBUG, DATABASE_URL etc.

# Apply migrations and create superuser
python manage.py migrate
python manage.py createsuperuser

# Run dev server
python manage.py runserver

# How to run tests
python manage.py test

# Contributing
Contributions are welcome. Please open an issue or a PR for larger changes