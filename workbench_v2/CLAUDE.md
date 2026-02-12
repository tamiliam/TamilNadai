# Agent Instructions — Tamil Nadai Workbench v2

Tamil grammar workbench for university collaboration. Django 5 + Tailwind CDN on Google Cloud Run, Supabase PostgreSQL.

---

## Lessons Learned (Applied from Thulivellam Retrospective)

These are documented failures from a sibling project. Read them. Follow them. Do not repeat them.

### 1. Test before you deploy — not the other way around

The workbench went through **7 Cloud Run deploys in a single session** (revisions 00015–00021). Several were fixing issues from the previous deploy: the comment box width took 3 iterations, the AI feature was completely redesigned after the first deploy. Each deploy takes 5+ minutes and costs real build minutes.

**Rule:** Run the app locally and verify changes before deploying. Use `python manage.py runserver` with the local SQLite database. Only deploy when you have tested the feature locally and are confident it works.

```bash
cd Tamil_Nadai/workbench_v2
python manage.py runserver
# Visit http://localhost:8000 and verify
```

**Rule:** Never deploy more than twice per feature. If you're on your third deploy for the same change, stop and rethink your approach.

### 2. Write tests alongside each feature

The test file (`core/tests.py`) is empty. The app has 204 rules, 334 sentences, a 3-role membership system, AI integration, and invitation workflows — all with zero test coverage. Thulivellam created 108 tests *before* shipping donor-facing features, and that safety net caught regressions throughout the sprint.

**Rule:** Every new view or model change must include at least one test. Before starting a new feature, write a test for the existing behaviour you're about to touch. After implementing, add tests for the new behaviour. Run tests before deploying:

```bash
python manage.py test core
```

**Minimum test coverage targets:**
- Every URL pattern resolves correctly
- Every view returns 200 for authorised users
- Permission decorators deny access to the wrong roles
- The review workflow (pending → review_1_done → accepted/rejected) works end-to-end
- AI suggestion endpoint returns valid JSON

### 3. Prototype UX in Stitch before coding templates

We have Stitch access and used it for HalaTuju (22 screens). For the workbench, templates were coded directly, resulting in multiple UI iteration cycles. The comment box layout was rewritten 3 times. The AI generation UI was built, thrown away, and rebuilt.

**Rule:** For any non-trivial UI change (new page, layout redesign, new component), create a Stitch screen first. Get visual approval. Then code to match the prototype. This is faster than deploy-test-fix-deploy.

### 4. Document as you go

The workbench has zero documentation — no README, no architecture doc, no deployment guide, no known issues. If a different developer (or agent) picks this up tomorrow, they have to reverse-engineer everything from the code.

**Rule:** Maintain these docs alongside code changes:
- `docs/architecture.md` — system overview, tech stack, data flow
- `docs/deployment.md` — how to deploy, env vars, common issues
- `docs/known-issues.md` — things that need fixing but aren't urgent

---

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

### Cloud Run Gotchas (from Thulivellam)

1. **SSL redirect:** `SECURE_SSL_REDIRECT` works here because `SECURE_PROXY_SSL_HEADER` is set. Without the proxy header, you get infinite redirect loops.
2. **Supabase connection:** Use Session Pooler URI (IPv4). Direct connection is IPv6 and fails on Cloud Run.
3. **CSRF:** `.run.app` must be in `CSRF_TRUSTED_ORIGINS`. Settings handle this automatically when `DATABASE_URL` is present.
4. **Static files:** `collectstatic` runs at Docker build time (in Dockerfile). WhiteNoise serves them.

---

## Working with This Codebase

### Before Any Change

1. Read this document
2. Check if the change touches templates → prototype in Stitch first
3. Check if the change touches views/models → write a test first
4. Run the app locally and verify before deploying

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

### Secrets

Secrets live **only** in Cloud Run environment variables. Never in files, never in code, never in `.env`. To update:

```bash
gcloud run services update tamilnadai --region asia-southeast1 \
  --update-env-vars "KEY=value"
```

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
