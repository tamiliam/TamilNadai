# Changelog

All notable changes to the Tamil Nadai Workbench are documented here.

## [1.0] — 2026-02-12

First public release.

### Features

- **204 grammar rules** from the Tamil Virtual University Style Guide (Book 169), organised into three categories: word joining (இலக்கண அமைப்பில் சொற்கள்), individual words (தனிச் சொற்களை எழுதும் முறை), and sandhi (சந்தி)
- **341 example sentences** (324 correct, 17 wrong) linked to specific rules
- **Two-reviewer workflow** — sentences go through pending, review_1_done, then accepted/rejected
- **AI sentence suggestions** — Gemini 2.0 Flash generates one sentence at a time; the user reviews and edits before saving
- **3-role membership** — Admin, Reviewer, Member with role-based access control
- **Invitation system** — token-based invites with 7-day expiry
- **Profile management** — name, email, affiliation, avatar upload
- **Per-rule discussions** — threaded comments with delete (own posts or admin)
- **LLM Evaluation** — benchmark Gemini, Claude, or GPT against the dataset with per-category scoring (Detection Rate, Correction Accuracy, Preservation Rate)
- **Research exports** — download the dataset (CSV/JSON) and evaluation results (CSV/JSON) for any logged-in member
- **Dashboard** — category breakdown, review progress, recent activity
- **Public pages** — About, Privacy, Terms, Cookies (no login required)
- **Palm-leaf manuscript design** — custom design system with semantic colour tokens

### Infrastructure

- Django 5 on Google Cloud Run (asia-southeast1)
- Supabase PostgreSQL (production), SQLite (local development)
- Tailwind CSS via CDN (no build step)
- WhiteNoise for static file serving
- 61 automated tests
- Ko-fi donation link ([ko-fi.com/elanjelian](https://ko-fi.com/elanjelian))

### Known Limitations

- Dataset is imbalanced — only 5% wrong sentences. More needed before HuggingFace publish.
- Avatars stored as base64 in the database. Works for small user counts.
- No CI pipeline yet.
