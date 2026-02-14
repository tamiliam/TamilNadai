# Agent Instructions — Tamil Nadai Workbench v2

Tamil grammar workbench for university collaboration. Django 5 + Tailwind CDN on Google Cloud Run, Supabase PostgreSQL.

---

## Project-Specific Rules

1. **Migration pattern**: SQL applied via Supabase MCP, then state-only Django migration. Never run `manage.py migrate` against Supabase in production.
2. **Test command**: `cd Tamil_Nadai/workbench_v2 && python manage.py test core`
3. **Deploy limit learned the hard way**: 7 deploys in one session for workbench v1. Follow the max-2-deploys rule in workspace `CLAUDE.md`.

General rules (testing, deployment discipline, Stitch prototyping, git, cleanup) are in the workspace-level `CLAUDE.md`.


## Architecture

| Component | Technology |
|-----------|-----------|
| Framework | Django 5.x |
| Database | Supabase PostgreSQL (production), SQLite (local dev) |
| CSS | Tailwind via CDN (no build step) |
| Hosting | Google Cloud Run (`asia-southeast1`) |
| Static files | WhiteNoise (collected at Docker build time) |
| AI | Google Gemini 2.0 Flash (sentence suggestions) |

### Key Files

| File | Purpose |
|------|---------|
| `core/views.py` | All view functions (~660 lines) |
| `core/models.py` | Source, Rule, Sentence, ReviewLog, Discussion, MemberProfile, Invitation |
| `core/services.py` | `suggest_sentence()` — AI generation via Gemini |
| `core/decorators.py` | `@require_role()` — permission decorator |
| `core/context_processors.py` | Injects `user_role`, `is_admin`, `is_reviewer_or_above`, `user_avatar` |
| `config/settings.py` | Django settings (dual SQLite/Postgres config) |
| `config/urls.py` | All URL patterns |
| `templates/` | Django templates with Tailwind classes |
| `templates/partials/` | Reusable template fragments (sentence_cards.html) |

### Role System

| Role | Level | Capabilities |
|------|-------|-------------|
| Admin | 3 | Everything: rules, sentences, members, roles, AI generation |
| Reviewer | 2 | Accept/reject sentences, propose sentences, discuss |
| Member | 1 | Propose sentences, discuss |

### Migration Pattern

SQL is applied directly via Supabase MCP, then a **state-only** Django migration is created to keep the ORM in sync. This means:
- Never run `python manage.py migrate` against Supabase in production
- Django migrations record state only (`migrations.AddField` etc.)
- The Supabase MCP `apply_migration` is the source of truth for DDL

---

## Deployment

**Service:** `tamilnadai` on Cloud Run (`asia-southeast1`)
**GCP Project:** `gen-lang-client-0871147736`
**URL:** `https://tamilnadai-90344691621.asia-southeast1.run.app`
**Supabase Project:** `wiyxydtqbkzafbbpstuq`

### Environment Variables (Cloud Run only — never in files)

| Variable | Purpose |
|----------|---------|
| `DEBUG` | `False` in production |
| `DJANGO_SECRET_KEY` | Session signing key |
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `GEMINI_API_KEY` | Google Gemini API key for AI features |

### Deploy Command

```bash
cd Tamil_Nadai/workbench_v2
gcloud run deploy tamilnadai \
  --source . --region asia-southeast1 --platform managed \
  --allow-unauthenticated --port 8080 --memory 512Mi \
  --min-instances 0 --max-instances 2
```

Env vars are already set on the service. Only use `--set-env-vars` when you need to change them.

### Django + Cloud Run Gotchas
- `SECURE_SSL_REDIRECT = False` — Cloud Run terminates SSL
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`
- Supabase: Use **Session Pooler** URI (IPv4), not Direct connection
- Custom domains: Set `CUSTOM_DOMAIN` env var → add to both `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`

---

## Working with This Codebase

### Database Changes

1. Apply SQL via Supabase MCP (`apply_migration`)
2. Create a state-only Django migration file
3. Update models.py to match
4. Test locally with SQLite (add field with defaults that work for both)

### Template Changes

The design system uses a palm-leaf manuscript metaphor:
- `leaf-*` — Background tones (parchment)
- `etch-*` — Text colours (inscribed text)
- `stylus-*` — Accent/gold tones
- `grain-*` — Border/divider tones (wood grain)
- `wood-*` — Navigation/header (dark wood)
- `palmgreen-*` — Accepted/positive
- `terracotta-*` — Rejected/negative

Tamil text uses `tamil` (sans) or `tamil-serif` CSS classes.

---

## Known Issues

1. **Base64 avatars in database.** Stored as data URIs in a TextField. Works for small user counts but bloats every response that loads avatar data. Consider Cloud Storage if user count exceeds ~50.
2. **No CI pipeline.** No GitHub Actions, no automated testing on push.

### Resolved (1.0 cleanup)

- ~~Zero test coverage~~ — 61 tests covering public pages, auth, roles, sentences, eval, exports.
- ~~No documentation~~ — README.md, CLAUDE.md, and HF dataset card written.
- ~~Stale SQL batch files~~ — Deleted (tmp_rules_batch_*.sql, tmp_sentences_batch_*.sql).
- ~~Unused `generate_sentences()` function~~ — Deleted from services.py.
- ~~DEBUG defaulting to True~~ — Changed to False.

