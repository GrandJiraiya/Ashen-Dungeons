# Ashen Dungeons — Next.js + Supabase + Vercel MVP Architecture Plan

This document maps the current Ashen Dungeons project direction into a modern web product plan using **TypeScript, Next.js, Supabase, and Vercel**. It is intentionally MVP-first while preserving a path to post-launch scale.

## 1) Frontend Plan

### Primary surfaces

1. **Marketing / Landing** (`/`)
   - Value proposition, gameplay loop summary, CTA to start playing.
   - Lightweight SEO content and screenshots.
2. **Auth** (`/login`, `/signup`, `/reset-password`)
   - Email magic link and OAuth options.
3. **Player Home** (`/dashboard`)
   - Save slots, latest run snapshot, progression summary.
4. **Run Setup** (`/runs/new`)
   - Select class, difficulty, starter loadout.
5. **In-Run Gameplay** (`/play/[runId]`)
   - Room progression, combat UI, loot/skills inventory, run log.
6. **Post-Run Summary** (`/runs/[runId]/summary`)
   - Outcomes, rewards, unlocked content.
7. **Leaderboard** (`/leaderboard`)
   - Global and friends filtering.
8. **Admin / Content Ops** (`/admin/content`, restricted)
   - Content pack version and publish tooling.

### Core component system

- `AppShell` (header, mobile nav drawer, notifications, profile menu).
- `SaveSlotCard`, `RunCard`, `ClassPicker`, `RoomNode`, `CombatPanel`, `SkillBar`, `LootModal`, `StatBadge`.
- `DataTable` for leaderboard/admin.
- `EmptyState`, `ErrorState`, `LoadingState` standardized for all async views.
- `ResponsiveBottomNav` for mobile gameplay controls.

### UI layout + responsive behavior

- **Desktop:** 2-column gameplay layout (`Map + Encounter` / `State + Actions`).
- **Tablet:** stacked sections with sticky action bar.
- **Mobile:** single-column with sheet-based drill-in (combat details, inventory, logs).
- Gameplay actions must be reachable with thumb-zone controls on 360px widths.
- Use `next/image`, route-level code splitting, and skeleton placeholders for smooth transitions.

### Key user flows

1. **New player:** Landing → Signup → Dashboard → Create run → First battle.
2. **Returning player:** Login → Dashboard restore from save slot → Continue run.
3. **Run completion:** Final boss → Summary → Leaderboard submission.
4. **Admin content push:** Login (admin) → Content validation preview → Publish version.

---

## 2) Backend Plan

### API style

Use a mixed model:
- **Next.js Server Actions** for trusted, UI-coupled mutations.
- **Route Handlers (`/api/...`)** for public or webhook-facing endpoints.
- **Supabase Edge Functions** for latency-sensitive or isolated tasks (score submission validation, anti-cheat checks, periodic cleanup).

### Suggested endpoints / actions

- `POST /api/runs` — create run.
- `POST /api/runs/:id/advance-room` — deterministic room transition.
- `POST /api/runs/:id/combat-action` — execute attack/skill/item command.
- `POST /api/runs/:id/loot/claim` — reward claim.
- `POST /api/save-slots/:id/restore` — restore run from slot.
- `GET /api/leaderboard` — paginated, filtered leaderboard view.
- `POST /api/webhooks/stripe` — payment event handling.

### Authentication and authorization

- Supabase Auth with:
  - email magic links for low-friction onboarding.
  - optional OAuth (Google/Discord) for faster retention loops.
- Role model:
  - `player`, `admin`, `service`.
- Authorization layers:
  1. Supabase RLS at table level.
  2. Server-side ownership checks for any mutation.
  3. Admin-only guards in middleware + DB policy checks.

### Business logic boundaries

- **Client:** presentation state only.
- **Server actions / API routes:** request validation + orchestration.
- **Domain layer (shared TS modules):** combat math, loot generation, progression rules.
- **Database:** source of truth for run state snapshots and inventory deltas.

### Webhooks and async events

- Stripe webhook → entitlement updates + audit log.
- Auth webhook/event hooks → profile initialization.
- Scheduled edge function/cron for leaderboard materialization and stale-run cleanup.

---

## 3) Supabase Database Design

### Tables (MVP)

1. `profiles`
   - `id uuid pk` (matches `auth.users.id`)
   - `display_name text`
   - `created_at timestamptz`
2. `save_slots`
   - `id uuid pk`
   - `profile_id uuid fk -> profiles.id`
   - `slot_index int` (1..3)
   - `label text`
   - `updated_at timestamptz`
   - unique `(profile_id, slot_index)`
3. `runs`
   - `id uuid pk`
   - `profile_id uuid fk -> profiles.id`
   - `save_slot_id uuid fk -> save_slots.id`
   - `status text` (`active|won|lost|abandoned`)
   - `class_id text`
   - `current_room_id text`
   - `hp int`, `mp int`, `gold int`
   - `seed bigint`
   - `started_at`, `ended_at`, `updated_at timestamptz`
4. `run_inventory`
   - `id bigint pk`
   - `run_id uuid fk -> runs.id`
   - `item_id text`
   - `quantity int`
5. `run_events`
   - `id bigint pk`
   - `run_id uuid fk -> runs.id`
   - `event_type text`
   - `payload jsonb`
   - `created_at timestamptz`
6. `leaderboard_entries`
   - `id bigint pk`
   - `profile_id uuid fk -> profiles.id`
   - `run_id uuid fk -> runs.id`
   - `score int`
   - `duration_seconds int`
   - `created_at timestamptz`
7. `content_versions`
   - `id uuid pk`
   - `version text unique`
   - `manifest jsonb`
   - `is_active boolean`
   - `published_by uuid fk -> profiles.id`

### Indexes

- `runs(profile_id, status)`
- `runs(save_slot_id)`
- `run_events(run_id, created_at desc)`
- `leaderboard_entries(score desc, created_at asc)`
- Partial: `runs(updated_at) where status = 'active'`

### Realtime needs

- Subscribe to:
  - `runs` row updates for active run synchronization.
  - `run_events` inserts for combat feed animation.
- Keep broadcast minimal; avoid subscribing to leaderboard in realtime for MVP (poll + cache instead).

### RLS policies (minimum)

- `profiles`: user can `select/update` own profile only.
- `save_slots`: owner-only CRUD.
- `runs`: owner-only read/write; no cross-account reads.
- `run_inventory`, `run_events`: only via join to owned `runs`.
- `leaderboard_entries`: public `select`, owner/service `insert`.
- `content_versions`: admin-only write, authenticated read.

### Storage buckets

- `public-assets` (read-only public: promotional images)
- `game-audio` (public read, admin/service write)
- `run-artifacts` (private: per-user uploads/log exports)

---

## 4) Vercel Deployment Plan

### Environment variables

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` (server only, never client-exposed)
- `SUPABASE_DB_URL` (if direct DB jobs needed)
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `NEXTAUTH_URL` or canonical app URL if using supplemental auth tooling
- `SENTRY_DSN`

### Preview deployments

- Enable for every PR.
- Bind preview env vars using isolated test Supabase project.
- Use branch-specific feature flags for incomplete systems.

### Production deployment

- `main` branch auto-promotes to production.
- Protect with required checks: typecheck, lint, tests, migration dry-run.
- Run DB migrations in CI before promoting if using migration pipeline.

### Domain and SSL

- Add custom domain in Vercel project settings.
- Force HTTPS and apex-to-www (or inverse) redirect consistency.
- Validate DNS records and SSL issuance before launch day.

### Build settings

- Framework preset: Next.js.
- Build command: `next build`.
- Output: default `.next`.
- Node runtime pinned to active LTS supported by Next.js version.

### Functions, cron, observability

- Use Vercel serverless/edge functions for API handlers.
- Vercel Cron Jobs:
  - stale run cleanup (daily)
  - leaderboard rollups (hourly)
- Add analytics:
  - Vercel Analytics + Web Vitals
  - Sentry (frontend + API route errors)
- Add uptime checks on `/api/health` and gameplay critical routes.

---

## 5) MVP Build Plan (Phased)

### Phase 0 — Setup

- Initialize Next.js TypeScript app and UI foundation.
- Configure Supabase projects (dev/staging/prod).
- Configure Vercel project + env variable sets.
- Add CI (lint, typecheck, unit tests).

### Phase 1 — Authentication

- Supabase Auth integration.
- Login/signup/reset flows.
- Profile bootstrap on first login.

### Phase 2 — Database

- Create core schema + indexes + RLS policies.
- Seed baseline content metadata.
- Add migration workflow and rollback verification.

### Phase 3 — Core gameplay features

- Run creation.
- Room traversal.
- Combat action loop.
- Loot and inventory updates.
- Run persistence/recovery.

### Phase 4 — Dashboard and progression UX

- Save slots UI.
- Run history and post-run summary.
- Profile stats and progression display.

### Phase 5 — Payments (optional MVP+)

- Stripe checkout for cosmetic/supporter tier.
- Entitlement table + webhook sync.
- Feature flag paid features.

### Phase 6 — Testing and hardening

- Unit tests for combat/progression logic.
- Integration tests for critical API flows.
- E2E smoke for auth + start-run + finish-run journey.
- Load and abuse checks on score submission endpoint.

### Phase 7 — Deployment and launch

- Production cutover checklist.
- Monitoring, alerts, and rollback plan.
- Soft launch with capped traffic.

---

## 6) Code Example Standard

When code is requested, default to:
- **TypeScript strict mode**.
- Next.js App Router patterns.
- Zod validation at API boundaries.
- Supabase generated types for DB safety.
- Server-only secret usage with no service-role leakage.
- Idempotent webhook handlers.
- Production logging with request context IDs.

---

## 7) Debugging Mode Protocol

When an error is provided, follow this sequence:
1. Classify layer: client, server action, API route, edge function, Supabase policy, Vercel deployment.
2. Identify likely root cause (schema drift, env mismatch, auth/session, RLS denial, bad cache, build/runtime mismatch).
3. Provide concrete fix steps in execution order.
4. Provide corrected code or deployment config.
5. Include verification commands and expected output.

---

## 8) Security Review Checklist

Run this review before release candidates:

1. **Keys/secrets**
   - No `SUPABASE_SERVICE_ROLE_KEY` in client bundles.
   - No secrets committed in repo history or `.env.example`.
2. **RLS coverage**
   - Every user table has RLS enabled.
   - Policies enforce ownership and role checks.
3. **Auth logic**
   - Protected routes redirect unauthorized users.
   - Server actions re-verify identity, not just client claims.
4. **API hardening**
   - Input validation on every mutation route.
   - Rate limits for login, combat actions, and leaderboard submission.
5. **Deployment security**
   - Production env vars only in Vercel encrypted settings.
   - Preview and production keys are separated.
6. **Database permissions**
   - Service role usage isolated to server-side modules.
   - Admin content routes require both role claim and DB policy support.

---

## 9) Launch Checklist

### Auth and authorization
- Login/signup/reset tested across devices.
- Protected routes verified for unauthorized access attempts.

### Database and policies
- RLS enabled and validated with test accounts.
- Backup/restore procedure documented.

### Environments and deployment
- All production env vars configured and validated.
- Domain + SSL active and redirect behavior confirmed.

### Observability
- Error logging active (server + client).
- Analytics dashboards receiving events.
- Alert thresholds configured for downtime/error spikes.

### Product quality
- Mobile responsiveness validated on small viewports.
- Core SEO metadata present on index/marketing pages.
- Performance budget checks completed (LCP/CLS targets).

### Operational readiness
- Rollback procedure tested.
- Incident response owner and runbook assigned.
- Post-launch monitoring window scheduled (first 24–72 hours).

