Short summary
- Purpose: Help an AI coding agent be productive in PrimeHaul OS (FastAPI + Jinja2 + SQLAlchemy multi-tenant app).

Quick facts
- Backend: FastAPI (single main app in app/main.py).
- ORM: SQLAlchemy models live in app/models.py (multi-tenant via Company.id / company_id).
- DB: app/database.py provides `get_db()` dependency. Use `alembic/` for migrations.
- Templates & frontend: Jinja2 templates in app/templates with vanilla JS and static assets in app/static.
- Auth: app/auth.py uses bcrypt + JWT (env var JWT_SECRET_KEY). Password rules are enforced in `validate_password_strength()`.
- AI integration: app/ai_vision.py uses OpenAI; set OPENAI_API_KEY in env.

What to know about architecture and patterns
- Multi-tenant model: every user-created record is scoped by `company_id`. Routes that serve customer surveys resolve company via middleware in `app/main.py` (URL pattern `/s/{company_slug}/{token}`). When editing or querying data, prefer using `get_db()` and always filter by `company_id` or use existing dependencies like `verify_company_access`.
- Job flow: customer-facing survey creates a `Job` (models.Job) identified by `token`. Many front-end pages use that token to retrieve and update job state.
- Templates: server-side rendering (Jinja2). Template context often expects `request.state.company` and `request.state.branding` injected by middleware — update templates cautiously when changing those keys.
- File uploads: stored in `app/static/uploads`. The app creates this dir at startup. Treat file paths as company-scoped when adding or reading.

Developer workflows & commands
- Local quick start (recommended):
  1. `pip install -r requirements.txt`
  2. `cp .env.example .env` and set required env vars: `DATABASE_URL`, `JWT_SECRET_KEY`, `OPENAI_API_KEY`, `MAPBOX_ACCESS_TOKEN`, `STRIPE_*`.
  3. `./start_test.sh` (starts the app with uvicorn and any local helper setup). Alternatively run:
     - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Database migrations: use Alembic (alembic.ini present). Typical commands:
  - `alembic revision --autogenerate -m "msg"`
  - `alembic upgrade head`
- Quick reset / staging helpers: `QUICK_RESET.py`, `QUICK_START_STAGING.md`, and `start_test.sh` are used by the team for reset/deploy tasks.

Project-specific conventions & gotchas
- Auth: `app/auth.py` uses `bcrypt` directly (not passlib). Use `hash_password()` and `verify_password()` helpers.
- JWT: tokens created via `create_access_token(user_id, company_id)` and validated using `decode_access_token()`; ensure `JWT_SECRET_KEY` is set in `.env` for local runs.
- Company resolution middleware: `resolve_and_check_company` in `app/main.py` populates `request.state.company`. Customer-facing routes depend on that state — do not bypass without explicit handling.
- DB sessions: always use `db: Session = Depends(get_db)` in route handlers and close/commit/refresh consistently (helper `get_or_create_job` shows the pattern).
- Logging SQL: toggle `echo=True` in `app/database.py` to help debug queries locally.

Integration points & external dependencies
- OpenAI (vision) — see `app/ai_vision.py`; requires `OPENAI_API_KEY`.
- Mapbox — templates use Mapbox; supply `MAPBOX_ACCESS_TOKEN`.
- Stripe — billing integrations in `app/billing.py`; set `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, and related price IDs.
- Storage: `app/static/uploads` and static serving via `app.mount('/static', StaticFiles(...))`.

Where to look first (high-impact files)
- `app/main.py` — central routes, middleware, startup logic, dev dashboard and app wiring.
- `app/models.py` — core data model and multi-tenant constraints (Company, Job, Room, Item, Photo).
- `app/database.py` — SQLAlchemy engine, `get_db()` dependency and connection pool settings.
- `app/auth.py` — password hashing and JWT utilities.
- `app/ai_vision.py`, `app/billing.py`, `app/marketplace.py` — important integrations.
- `alembic/` — migration history and patterns for schema changes.

How to make safe edits
- Preserve multi-tenant filters: when adding queries, always filter by `company_id` or use existing helpers (do not return cross-company data).
- Template changes: preserve `request.state.branding` keys and `company_slug` expectations to avoid breaking customer views.
- Backwards compatibility: migrations are used in production; create an Alembic revision whenever you change models.

If you need more context
- Inspect `README.md` for business context and the dev quick-start. For runtime debugging, check `DEV_DASHBOARD_PASSWORD` and `STAGING_MODE` flags in `app/main.py`.

Ask me to refine any section or add examples (e.g. common PR patterns, mutation examples, or sample queries).
