# Tamil Nadai Workbench v2 — Project Retrospective

**Version:** 1.0
**Last updated:** 2026-02-12
**Build duration:** 8 sessions across 5 days (2026-02-08 to 2026-02-12)

Tamil Nadai is a collaborative workbench for Tamil language experts to review, validate, and benchmark Tamil writing convention rules. It produces a curated dataset that benchmarks how well LLMs understand Tamil grammar — specifically word joining, sandhi (vallinam doubling), and individual word conventions. The rules come from the Tamil Virtual University Style Guide (Book 169, tamilvu.org).

This retrospective covers the full build from zero to 1.0.

---

## Project Timeline

| Session | Date | Deploys | What Shipped |
|---------|------|---------|-------------|
| 1 | Feb 8 | 00001–00014 | Core: rules, sentences, review workflow, dashboard |
| 2 | Feb 8 | 00014 | Membership (3 roles, profiles, invitations), pagination |
| **3** | **Feb 8** | **00015–00021** | **Prev/next nav, AI redesign, avatars, sentence cards. 7 deploys in one session.** |
| 4 | Feb 8 | 00022–00023 | Applied Thulivellam lessons: CLAUDE.md, static pages, first 29 tests |
| 5 | Feb 11 | 00024–00025 | Sentence attribution, LLM Evaluation module (44 tests) |
| 6 | Feb 11 | 00026 | Research exports (CSV/JSON), 61 tests |
| 7 | Feb 11 | 00027–00031 | Eval timeout fix, Preservation Rate, nav cleanup, Ko-fi, HF dataset prep |
| 8 | Feb 12 | 00032 | 1.0 cleanup, README, .gitignore, deploy |

**Total:** 32 Cloud Run revisions. **Ideal:** ~12 (one per feature).

---

## What Went Well

**The Thulivellam retrospective paid off immediately.**
Session 3 burned 7 deploys on UI tweaks. Session 4 started by reading the Thulivellam retrospective and creating CLAUDE.md with explicit rules. From Session 5 onwards, every feature was a single deploy. The retro literally cut deploy waste by 80%.

**Supabase MCP for dual-database development.**
Production runs on Supabase PostgreSQL; local dev uses SQLite. Schema changes are applied via Supabase MCP, then recorded as state-only Django migrations. This pattern avoided ever running `manage.py migrate` against production and kept the ORM in sync without risk.

**AI as assist, not replace.**
The original AI feature (Session 1–2) generated 5 sentences in batch, dumped them into the database. It was redesigned in Session 3 as a single-sentence AJAX suggestion that fills the input field for the human to review and edit. This "AI suggests, human decides" pattern was more useful, less risky, and used fewer API credits.

**Tests written mid-project, not at the end.**
Session 4 wrote the first 29 tests. By 1.0, there were 61. They caught the `SECURE_SSL_REDIRECT` regression immediately when the DEBUG default was changed in the cleanup session. Without tests, that bug would have gone to production.

**Eval module reused the dataset it was benchmarking.**
The LLM Evaluation feature tests Gemini/Claude/GPT against the workbench's own dataset. This created an immediate feedback loop: contributors add sentences, the eval shows whether LLMs handle them correctly, which motivates adding harder cases. The dataset and the benchmarking tool are the same product.

**The palm-leaf design system.**
Defining a design vocabulary early (leaf, etch, stylus, grain, wood, palmgreen, terracotta) made all subsequent UI work faster. Instead of debating colours for each feature, the tokens were just applied. It also gave the app a distinctive identity — it doesn't look like a generic Bootstrap dashboard.

---

## What Went Wrong

### Session 3: The 7-Deploy Disaster

This session is the single biggest lesson from the project.

**What happened:** Prev/next navigation, AI panel redesign, comment box width, invite expiry display, avatar upload, and sentence cards — all shipped in one session, each requiring its own deploy. The AI feature was built, thrown away, and rebuilt. The comment box width took 3 iterations.

**Why it happened:**
1. No local testing. Changes went straight to Cloud Run.
2. No UI prototype. Templates were coded blind, then adjusted after seeing the result live.
3. Feature creep. What started as "add prev/next buttons" expanded to "also redesign AI, also fix comments, also add avatars."

**The cost:** 7 deploys at ~5 minutes each = 35 minutes of waiting. But the real cost was the 3+ hours of coding wasted features that got thrown away (batch AI generation) and tweaking CSS that should have been prototyped first.

**Rule that emerged:** Test locally before deploying. Prototype UI in Stitch before coding templates. Never deploy more than twice per feature.

### Documentation Written Last

The project had zero documentation until Session 4 (CLAUDE.md) and zero public docs until Session 8 (README.md). CLAUDE.md was written as a corrective measure after the Session 3 disaster, not as a natural part of the build process. The README was written during cleanup, relying on memory and git archaeology.

**The problem this creates:** If I'm unavailable tomorrow, nobody can set up the project, understand the architecture, or deploy it without reverse-engineering the code.

**Rule that emerged:** Document as you build. Every feature should update the relevant doc before it's considered done.

### Dead Code Accumulated Silently

The 1.0 cleanup found:
- 10 stale SQL files from the initial data import
- An entire unused function (`generate_sentences()`, 90 lines) from the pre-Session-3 batch AI design
- A hardcoded path in `prepare_dataset.py` pointing to a temporary MCP output file
- DEBUG defaulting to True (unsafe for production)

None of this was caught earlier because there was no cleanup pass built into the process. Each session left behind its artifacts, and nobody went back to check.

**Rule that emerged:** When you replace a feature, delete the old code in the same session. Don't leave dead code for "cleanup later." There is no later — only the cleanup you do right now.

### Dataset Imbalance Not Addressed

The dataset has 324 correct sentences and only 17 wrong sentences (5%). This was known from Session 6 but not acted on. The AI suggestion feature defaults to generating "correct" sentences because they're easier to validate. Wrong sentences require more careful curation — the sentence must violate the specific rule, not just be generally wrong.

**Why it matters:** A dataset with 95% correct sentences is almost useless for benchmarking. Any model that returns the input unchanged scores 95% accuracy. The wrong sentences are what make the benchmark meaningful.

**What should have happened:** A deliberate "wrong sentence sprint" alongside the correct sentences, possibly with a different AI prompt that generates plausible mistakes for each rule.

### Eval Timeout Discovered in Production

The LLM Evaluation feature made synchronous API calls to Gemini for every sentence. With 341 sentences, this took 15+ minutes — well past Cloud Run's default request timeout. The request would silently die, and the user saw no results.

**Fix:** Threading for background evaluation + a `status` field on EvalRun (pending/running/completed/failed) + `--no-cpu-throttling` on Cloud Run so background threads aren't killed.

**What should have happened:** Any feature that calls an external API in a loop should use background processing from the start. This is true for 10 items or 10,000 — the pattern is the same.

### Settings Tied to Wrong Signals

`SECURE_SSL_REDIRECT` was set to `not DEBUG`. When the 1.0 cleanup changed DEBUG to default to False (correct for safety), SSL redirect activated in the test environment, breaking all 61 tests with 301 redirects.

**Fix:** Tied SSL redirect to `DATABASE_URL` presence instead of DEBUG. This correctly distinguishes "running on Cloud Run" from "running locally or in tests."

**Rule that emerged:** Production behaviour should be gated on production signals (DATABASE_URL, a PRODUCTION env var), not on the absence of a dev signal (DEBUG). They're not the same thing.

---

## Key Technical Lessons

### 1. AI assist > AI automate

The batch generation approach (generate 5 sentences, save them all) was less useful than the single-sentence suggestion (generate one, let the human edit). Users don't want to review a batch — they want help filling a blank field. Design AI features as assistants that fill inputs, not robots that fill databases.

### 2. Background processing for any external API loop

If your feature calls an external API more than once in a request, use background processing. Not because 3 calls are slow, but because the pattern is the same whether it's 3 or 300. Build it right the first time. Cloud Run will kill your request at the timeout regardless.

### 3. Gate production behaviour on production signals

Use `bool(os.environ.get("DATABASE_URL"))` or a dedicated `PRODUCTION=true` env var. Don't use `not DEBUG`. DEBUG might be False in tests, in staging, or because someone forgot to set it. A production signal should be explicitly present, not inferred from the absence of a dev flag.

### 4. Delete replaced code immediately

When you redesign a feature (batch AI → single AI), delete the old function in the same session. The old code will never be needed — you replaced it for a reason. Leaving it creates confusion about which code is active and adds to the cleanup burden later.

### 5. UTF-8 BOM for CSV with Tamil text

Excel on Windows doesn't detect UTF-8 encoding in CSV files. Tamil text appears as garbled characters. Adding a BOM (byte order mark, `\ufeff`) at the start of the file tells Excel to use UTF-8. This is a one-line fix but took debugging to discover.

### 6. The palm-leaf design system approach works

Define your design vocabulary (colour tokens, typography classes, status colours) before building templates. Use semantic names (leaf, etch, stylus) not raw values (#f5e6c3). This makes every subsequent UI decision faster and keeps the app visually consistent without a dedicated designer.

### 7. Supabase MCP + state-only Django migrations

For projects using Supabase as the production database: apply DDL via MCP, create Django migrations that only record the state change (no RunSQL), and never run `migrate` against production. This keeps the ORM happy while letting Supabase handle the actual schema.

---

## Rules for Future Projects

These are extracted from the failures above and from the Thulivellam retrospective. They apply to all Django + Cloud Run + Supabase projects.

| # | Rule | Source |
|---|------|--------|
| 1 | **Test locally before deploying.** `runserver` + browser. Never deploy more than twice per feature. | Thulivellam retro, Tamil Nadai Session 3 |
| 2 | **Write tests alongside features.** Run `manage.py test` before deploying. | Thulivellam retro, Tamil Nadai Session 4 |
| 3 | **Prototype UI in Stitch before coding templates.** | Tamil Nadai Session 3 |
| 4 | **Document as you build.** Update docs before considering a feature done. | Thulivellam retro, Tamil Nadai Session 8 |
| 5 | **Never put secrets in files.** Cloud Run env vars only. | Thulivellam retro |
| 6 | **Write a retrospective when you ship.** Not later. Not next session. Now. | Tamil Nadai 1.0 (this document was almost forgotten) |
| 7 | **Delete replaced code immediately.** If you rebuild a feature, delete the old one in the same session. | Tamil Nadai Session 8 (10 stale files, 90-line dead function found at cleanup) |
| 8 | **Gate production behaviour on production signals.** Use `DATABASE_URL` or `PRODUCTION=true`, not `not DEBUG`. | Tamil Nadai Session 8 (SSL redirect broke all tests) |
| 9 | **Use background processing for any external API loop.** Don't wait for the timeout to teach you. | Tamil Nadai Session 7 (eval timeout) |
| 10 | **Balance your dataset from the start.** If you're building a benchmark, plan for negative examples from day one. | Tamil Nadai 1.0 (95% correct, 5% wrong is not a benchmark) |

---

## If Starting Over

1. **Start with the dataset design, not the UI.** Define what a balanced dataset looks like (ratio of correct to wrong, coverage per category, minimum sentences per rule) before building the workbench features. The workbench exists to produce the dataset — the dataset requirements should drive the features.

2. **Build the eval module in Session 2, not Session 5.** Having evaluation results early creates a feedback loop that motivates contributors and reveals which rules need more examples.

3. **Single-session features only.** If a feature can't be built, tested, and deployed in one session, it's too big. Break it down. Session 3 tried to do 6 features and produced 7 deploys.

4. **Wrong sentences need a dedicated workflow.** Generating wrong sentences is harder than generating correct ones. The AI prompt needs to violate a *specific* rule, not just produce bad Tamil. This might need a different UI flow — "generate a mistake for this rule" rather than "generate a sentence."

5. **Retrospective is part of the release, not after it.** This document should be written before the deploy command, not after someone asks "what about a retrospective?"

---

## Summary

Tamil Nadai 1.0 shipped with 204 rules, 341 sentences, a 3-role collaboration system, LLM evaluation, research exports, and a curated dataset card. The biggest failure was Session 3 (7 deploys, wasted code). The biggest save was the Thulivellam retrospective, which cut deploy waste immediately after being applied.

The dataset imbalance (95% correct) is the most important outstanding issue — it determines whether the benchmark is useful or decorative. Everything else (CI, avatars, scaling) can wait.

The most important lesson: **a retrospective that isn't part of your process will be forgotten.** It was almost forgotten here. Rule 6 now exists to prevent that.
