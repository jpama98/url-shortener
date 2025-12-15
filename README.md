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
