# Ashen Dungeons — Release Status Report

**Report Date:** April 23, 2026  
**Report Time:** 12:30 PM America/Chicago  
**Project Phase:** Foundation / Pre-Prototype  
**Overall Status:** Yellow  
**Release Readiness:** Not ready for internal alpha  
**Primary Focus:** Boot reliability, schema reproducibility, foundation completion

---

## Executive Summary

Ashen Dungeons is progressing well from an architecture and planning standpoint, but it is still in the foundation phase rather than the playable prototype phase.

The repository now contains the correct high-level application shape:
- Flask app factory
- config and extensions
- blueprint structure
- DB session wiring
- Alembic environment
- ORM model files
- repository layer
- content loader scaffolding

This is a strong starting point and indicates the rebuild is on the right path.

However, the project is **not yet operationally stable**. The app is likely not booting cleanly due to content-loading path and missing content-file issues. In addition, Alembic is not yet fully positioned to generate the intended schema until all real models are exposed through the model package. The initial migration has also not yet been generated and committed.

At this point, the project should be managed as a **foundation-completion effort**, not as a gameplay or content-production effort.

---

## Current Health Assessment

### Schedule Health: Yellow
The project is moving in the correct order and the repo is no longer empty, but several foundational tasks still block all downstream work.

### Technical Health: Yellow
Architecture decisions are sound, but operational readiness is incomplete. The app, migration flow, and content loading need to be stabilized before gameplay work continues.

### Scope Health: Green
Scope is currently well controlled. Product decisions are locked for MVP, and there is no evidence of major scope creep.

### Release Health: Red
The project is not ready for internal alpha, external testing, or any public deployment beyond placeholder infrastructure.

---

## Locked Product Decisions

The following decisions are now considered stable for MVP:

### Game Direction
- Browser-based single-player RPG
- Dark fantasy / gritty dungeon crawler
- Classic JRPG turn-based combat
- One hero per run
- Node / room based progression
- Hand-authored dungeon content first
- Three player classes
- One act with a final boss
- MP-based skills
- Death wipes only the current run

### Identity / Save Model
- Anonymous / local profile first
- Multiple save slots per local profile
- No account system in MVP

### Technology Stack
- Python + Flask
- SQLAlchemy
- Alembic
- Jinja templates
- Vanilla JavaScript
- Howler.js for audio
- PostgreSQL
- Railway + Supabase + Cloudflare R2 target stack

---

## Completed Work to Date

### Planning and Architecture
Completed:
- full fresh-start rebuild decision
- repo skeleton definition
- system architecture planning
- MVP scope definition
- phased implementation plan
- contractor task breakdown
- GitHub issue backlog
- SPEC-1 architecture/design document

### Codebase Structure
Present in repo:
- `create_app()` structure
- `app.py`
- `wsgi.py`
- blueprints:
  - site
  - game
  - api
  - admin
- DB session layer
- Alembic environment
- ORM model files
- repository files
- content loader files

This means the project is structurally established, even though it is not yet functionally complete.

---

## What Is Working Well

- The rebuild is no longer conceptual; the repository has meaningful structure.
- The architecture is aligned with long-term maintainability.
- The project is avoiding the trap of patching the old repo indefinitely.
- The content-driven approach is correct for a game that will need balancing and iteration.
- The schema direction is appropriate for save slots, run state, inventory, encounters, leaderboard, and asset mapping.
- The issue breakdown is good enough to hand to contractors in sequence.

---

## Current Blockers

### 1. App boot reliability is not yet guaranteed
The content-loading system expects a complete content pack, but the visible repo state indicates that content files and schemas are not yet fully aligned.

**Impact:** app startup may fail before any real gameplay work can proceed.

### 2. Content root / authored-data organization still needs to be finalized
The correct long-term structure is:
- Python content loader code stays under `src/ashen_dungeons/content/`
- authored JSON data and schemas live under top-level `/content`

**Impact:** until this is stabilized, content loading remains fragile.

### 3. Alembic model discovery is incomplete
Model files exist, but the model package still needs to expose all real ORM models so Alembic autogeneration includes the actual schema rather than only placeholder metadata.

**Impact:** initial migration generation may be incomplete or incorrect.

### 4. Initial migration has not been committed
The repo still needs its first real schema migration under `migrations/versions/`.

**Impact:** the database is not yet reproducible from zero.

### 5. No gameplay systems are implemented yet
Routes remain placeholder-level and there is not yet a profile/save/run/gameplay loop.

**Impact:** the repo is not yet testable as a game.

---

## Immediate Priority

The highest priority is **not** combat, content depth, UI polish, or balancing.

The highest priority is:

### Foundation Completion
1. Make the app boot cleanly
2. Make Alembic see the real schema
3. Generate and commit the first real migration

This is the critical path that unlocks all meaningful downstream development.

---

## Recommended Next 3 Commits

### Commit 1 — Make the app boot reliably
Deliverables:
- explicit `CONTENT_ROOT`
- top-level `/content`
- placeholder content files
- placeholder schema files
- loader path aligned with config

Success criteria:
- app starts locally
- `/health` returns 200
- content loader succeeds with placeholder data

### Commit 2 — Make Alembic see the real schema
Deliverables:
- `db/models/__init__.py` imports all real ORM models
- `migrations/versions/` exists
- committed cache files removed
- metadata verification passes

Success criteria:
- `Base.metadata.tables.keys()` contains intended game tables

### Commit 3 — Generate and apply the first real migration
Deliverables:
- initial Alembic revision generated
- migration reviewed and committed
- `alembic upgrade head` succeeds
- app still boots after migration

Success criteria:
- database schema is reproducible from zero

---

## Recommended Development Sequence After Foundation

Once the three foundation commits are complete, development should continue in this order:

1. Initial MVP content pack
2. Anonymous profile initialization
3. Save slot flow
4. Run creation
5. Hand-authored dungeon progression
6. Combat engine
7. Rewards / loot / progression
8. Leaderboard
9. Assets and audio
10. Hardening and automated tests

This preserves build stability and avoids rework.

---

## Risks

### Risk: Starting gameplay too early
If combat or traversal is implemented before boot and migration stability are fixed, the team will build features on unstable infrastructure.

**Mitigation:** complete the three foundation commits first.

### Risk: Content and code remain mixed
If authored content stays embedded under the Python package instead of a clear top-level content directory, future editing and deployment workflows will become messy.

**Mitigation:** separate code from authored data now.

### Risk: Migration drift
If the first migration is delayed while models continue changing, the schema may drift and the first revision becomes harder to trust.

**Mitigation:** generate the initial migration immediately after model exposure is fixed.

### Risk: Team confusion
Without a status document, implementation can drift into UI or gameplay work prematurely.

**Mitigation:** use this report plus the issue backlog to control work order.

---

## Release Outlook

### Internal Alpha Readiness
Not ready.

### What must be true before internal alpha can be considered
- app boots cleanly
- content loads reliably
- schema migrates from zero
- anonymous profile flow exists
- save/load exists
- run creation exists
- at least one playable dungeon/combat loop exists

### Forecast
If foundation work is completed cleanly, the project can transition from architecture mode to playable-system implementation mode without major rework.

---

## Management Recommendation

Treat the current repo as **successful early groundwork**, but do not mistake structure for readiness.

The correct management stance is:

- continue
- do not pivot
- do not widen scope
- do not jump ahead to polish
- finish the foundation exactly in order

The project is on track **if** the next effort is disciplined and focused on the boot/migration/content-root issues first.

---

## Bottom Line

Ashen Dungeons is **architecturally healthy** but **operationally incomplete**.

This is not a failing project.  
It is a correctly shaped project that still needs its foundation locked before gameplay can begin.

### Current Status
**Yellow — progressing, but blocked by foundational readiness issues**

### Immediate Next Action
**Complete Commit 1, Commit 2, and Commit 3 before starting gameplay systems**