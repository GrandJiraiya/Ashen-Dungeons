# Ashen Dungeons

Ashen Dungeons is a fresh-start browser RPG rebuild using Flask, PostgreSQL, Alembic, and a content-driven game architecture.

## Current state
This repository is in **foundation / pre-prototype** stage.

Implemented so far:
- Flask app factory
- config loading
- blueprint registration
- content loader
- DB session wiring
- first Alembic migration scaffold
- root developer workflow files

Not implemented yet:
- dungeon progression
- combat loop
- save slots UI
- leaderboard flow

## Local Python workflow

### 1. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create env file
```bash
cp .env.example .env
export PYTHONPATH=src
```

### 4. Start PostgreSQL
You can use a local PostgreSQL install or Docker Compose:

```bash
docker compose up -d db
```

### 5. Apply migrations
```bash
alembic upgrade head
```

### 6. Run the app
```bash
python app.py
```

App URLs:
- http://127.0.0.1:5000/
- http://127.0.0.1:5000/health

## Docker workflow

### Start database only
```bash
docker compose up -d db
```

### Build and run app + db
```bash
docker compose up --build
```

### Stop services
```bash
docker compose down
```

## Makefile commands
```bash
make dev
make test
make lint
make seed
make docker-up
make docker-down
```

## Notes
- Set `PYTHONPATH=src` when running locally outside Docker.
- This repo does not yet contain the full gameplay loop.
- The next major milestones are anonymous profile init, save slots, dungeon progression, and combat.
