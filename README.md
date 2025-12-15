# URL Shortener Service

A scalable URL shortener built with FastAPI, PostgreSQL, Redis caching, rate limiting, and Docker.
Designed to demonstrate production-ready backend engineering skills (Amazon SDE Intern level).

## Features
- URL shortening
- Fast redirects (302)
- Click analytics
- Rate limiting (SlowAPI)
- Redis caching
- Docker Compose (App + Postgres + Redis)
- Async SQLAlchemy
- Pytest test

## Run Locally
```bash
uvicorn app.main:app --reload
```

## Run with Docker
```bash
docker compose up --build
```

## API Docs
http://localhost:8000/docs
## Migrations (Alembic)
```bash
# 1) start postgres + redis
docker compose up -d db redis

# 2) run migrations (local)
alembic upgrade head
```

## Auth + Per-user Dashboard
- Register/Login with JWT access + refresh tokens
- Short URLs are owned by a user
- Dashboard: `/api/dashboard/summary`

## Background Click Logging (Async Redis Queue)
Redirects enqueue click events into Redis (fast), and a background worker persists them to Postgres.
