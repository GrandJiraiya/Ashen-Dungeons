# Ashen Dungeons — Project Status

**Status Snapshot:** April 23, 2026 at 12:30 PM (UTC-05:00 / America/Chicago)

---

## Current Position

Ashen Dungeons is in the **foundation / architecture stage**.

The new repository is no longer empty. It already includes:
- Flask app factory structure
- configuration module
- extensions module
- blueprint structure
- database session wiring
- Alembic environment
- ORM model files
- repository files
- content loader code

This means the project has moved past “blank repo” and into **structured backend scaffolding**.

However, it is **not yet at playable prototype stage**.

---

## What Has Been Decided

### Product Direction
- Browser-based single-player RPG
- Dark fantasy / gritty dungeon crawler
- Classic JRPG turn-based battles
- One hero character
- Node / room based progression
- Hand-authored dungeon content first
- Three player classes
- One act with a final boss
- Skills use MP
- Death loses only the current run

### Identity / Save Model
- Anonymous / local profile first
- No account system in MVP
- Multiple save slots per local profile

### Recommended Stack
- Python + Flask
- SQLAlchemy
- Alembic
- Jinja templates
- Vanilla JavaScript
- Howler.js for audio
- Railway for app hosting
- Supabase Postgres for database
- Cloudflare R2 for images/audio storage

### Budget Target
- Designed to stay within **$50/month**

---

## What Has Already Been Produced

### Repo Skeleton
A full fresh-start repo skeleton was created, including:
- `src/ashen_dungeons/`
- content placeholders
- assets placeholders
- tests
- docs
- migrations
- infra
- `app.py`
- `wsgi.py`
- `.env.example`
- `pyproject.toml`

### SPEC-1-Ashen-Dungeons
The architecture/design spec was drafted with these sections:
- Background
- Requirements
- Method
- Implementation
- Milestones
- Gathering Results

### Contractor Planning
A contractor-ready execution plan was created, including:
- phased implementation plan
- GitHub milestone structure
- MVP definition of done

### GitHub Backlog
A GitHub issues backlog was created, including:
- issue titles
- descriptions
- acceptance criteria
- suggested labels

---

## Current Repo Status

### What Is Already Present
- `create_app()` exists
- `app.py` and `wsgi.py` exist
- blueprints exist for:
  - site
  - game
  - api
  - admin
- DB session wiring exists
- Alembic environment exists
- model files exist
- repository files exist
- content loader code exists

### What Is Not Ready Yet
- content loading path is not fully aligned
- content files are incomplete
- schema files are incomplete
- the app likely does not boot cleanly yet
- Alembic is not yet seeing the full real model set
- the first real migration has not been completed and committed
- routes are still placeholders
- no gameplay systems are implemented yet
- no save/load game loop is implemented yet
- no combat loop is implemented yet

### Overall Status
The project is at:

**“Strong architecture scaffold, but still in bootability + migration foundation phase.”**

---

## Immediate Blockers

### Blocker 1 — Content root mismatch
The application loads content during startup, but the authored content files and schemas are not yet fully in the right place and not yet complete.

### Blocker 2 — Missing placeholder content pack
The loader expects:
- `classes.json`
- `rooms.json`
- `enemies.json`
- `bosses.json`
- `items.json`
- `loot_tables.json`
- `shops.json`
- `status_effects.json`
- `ui_text.json`
- `audio_map.json`

These all need to exist with valid structure before clean boot can be guaranteed.

### Blocker 3 — Model discovery for Alembic
Alembic metadata wiring exists, but the model package still needs to expose all real ORM models so autogeneration can see the intended schema.

### Blocker 4 — No committed initial migration
The project still needs its first real Alembic migration revision committed under `migrations/versions/`.

---

## Next 3 Commits

### Commit 1 — Make the app boot reliably
#### Goal
Make `create_app()` start without crashing on content loading.

#### Actions
- Add explicit `CONTENT_ROOT` config
- Move authored JSON files to top-level `/content`
- Keep Python content loader code in `src/ashen_dungeons/content/`
- Add missing placeholder content files
- Add missing placeholder schema files
- Update config and extension wiring

#### Done when
- app boots locally
- `/health` returns 200
- content loader succeeds with placeholder data

---

### Commit 2 — Make Alembic see the real schema
#### Goal
Expose all actual ORM models to `Base.metadata`.

#### Actions
- Update `src/ashen_dungeons/db/models/__init__.py`
- Import:
  - Player
  - SaveSlot
  - Run
  - InventoryItem
  - Encounter
  - LeaderboardEntry
  - AssetManifest
- Create `migrations/versions/`
- Remove committed `__pycache__/`
- Verify metadata includes the intended tables

#### Done when
- `Base.metadata.tables.keys()` shows the expected schema tables

---

### Commit 3 — Generate and apply the first real migration
#### Goal
Make the schema reproducible from zero.

#### Actions
- Run Alembic autogenerate
- Review generated migration
- Apply migration locally
- Verify expected tables exist
- Confirm app still boots after migration

#### Done when
- migration file exists under `migrations/versions/`
- `alembic upgrade head` succeeds
- expected tables exist
- app still boots

---

## Best Next Development Sequence

After those 3 commits, continue in this order:

1. Create initial MVP content pack
2. Implement anonymous profile initialization
3. Implement save slots
4. Implement run creation
5. Implement dungeon node progression
6. Implement combat engine
7. Implement rewards / loot / progression
8. Implement leaderboard
9. Implement assets and audio
10. Harden with tests and release flow

---

## Current Best Summary

Ashen Dungeons is in a good place **architecturally**, but not yet in a good place **operationally**.

The next milestone is not “make gameplay fun” yet.  
The next milestone is:

**Make the app boot cleanly, make the schema discoverable, and commit the first real migration.**

Once that is done, the project becomes a real runnable foundation instead of just a well-shaped scaffold.

---

## Short Version

### You have:
- the right architecture
- the right folder structure
- the right database direction
- the right content-driven design
- the right implementation roadmap

### You do not yet have:
- clean boot reliability
- complete content placeholders
- fully exposed ORM metadata
- initial migration committed
- playable systems

### Therefore:
The project is **on track**, but still in **foundation completion mode**.

---

## Recommended Immediate Action

Complete these in order:
1. Commit 1 — content boot fix
2. Commit 2 — model exposure for Alembic
3. Commit 3 — first migration

After that, move into:
- content pack
- profile/save flow
- dungeon traversal
- combat

---