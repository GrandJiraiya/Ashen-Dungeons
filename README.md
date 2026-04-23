# Ashen Dungeons — Repo-Integrated Local Flask Build

This is a self-contained **local** Flask build shaped like the planned `ashen_dungeons`
repository architecture. It is designed to drop into the repo and run without:
- PostgreSQL
- Alembic
- Supabase
- Cloudflare R2
- external APIs
- internet access

## What it includes
- Flask app factory
- blueprint-based routes
- top-level content pack
- 3 classes
- 10-room act
- turn-based combat
- loot, equipment, consumables
- local save slots (JSON files)
- local leaderboard (JSON file)

## Quick start
1. Install Flask if needed.
2. Run `app.py`
3. Open `http://127.0.0.1:5000`

## Notes
This build is intentionally **local-first** and **Pythonista-friendly**.
It is meant to help you test the game loop while keeping the project structure aligned
with the main repo.

## Suggested merge strategy
Copy these folders/files into your `Ashen-Dungeons` repo:
- `app.py`
- `wsgi.py`
- `content/`
- `src/ashen_dungeons/`
- `templates/` are already inside package under `web/templates`
- `static/` are already inside package under `web/static`
