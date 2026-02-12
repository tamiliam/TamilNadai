# Contributing to Tamil Nadai (தமிழ் நடை)

Thank you for your interest in helping build a gold-standard Tamil grammar benchmark. This guide explains how to contribute as a **language expert** (adding and reviewing sentences) and as a **developer** (improving the platform).

---

## For Language Experts

### Getting access

Tamil Nadai uses an invitation system. An existing member will send you an invitation link. Click the link, create your account, and you're in.

Invitations expire after 7 days. If yours has expired, ask the person who invited you to send a new one.

### Your role

| Role | What you can do |
|------|----------------|
| **Member** | Add sentences, join discussions |
| **Reviewer** | Everything a Member can do, plus accept or reject sentences |
| **Admin** | Everything a Reviewer can do, plus manage members and rules |

You'll start as a Member or Reviewer depending on your invitation.

### Adding sentences

This is the most valuable contribution. Each grammar rule needs example sentences — both **correct** (follows the rule) and **wrong** (violates the rule).

**How to add a sentence:**

1. Go to any rule page (browse Rules, then click a rule)
2. Scroll to the sentence section
3. Choose "Correct" or "Wrong" from the dropdown
4. Type your sentence in the text field
5. Click "Add"

**What makes a good sentence:**

- A complete sentence with a subject and verb, not just a word or phrase
- Short — under 10 words is ideal
- Naturally sounds like something a Tamil speaker would write
- For "wrong" sentences: the mistake should be exactly the kind of error this specific rule addresses. Don't just write bad Tamil — write Tamil that makes the specific mistake this rule is about.

**Using AI suggestions:**

Click the "Suggest" button to have AI generate a sentence. The suggestion fills the text field — **always review and edit it** before saving. The AI doesn't always get it right, which is exactly why we need human experts.

### Reviewing sentences

If you're a Reviewer or Admin:

1. Go to the Review Queue (in the navigation menu)
2. You'll see sentences waiting for review
3. Read the sentence and its associated rule
4. Click "Accept" if the sentence correctly demonstrates (or correctly violates) the rule
5. Click "Reject" if it doesn't

Each sentence needs two reviews before it's fully accepted. Your review is the first or second step.

### Discussions

Every rule has a discussion thread. Use it to:

- Ask questions about how a rule should be interpreted
- Suggest improvements to rule descriptions
- Debate edge cases

### The dataset we're building

Every sentence you add and review becomes part of the **Tamil Grammar Benchmark** — a dataset that tests whether AI language models understand Tamil writing conventions. The better our sentences, the more useful the benchmark.

We especially need more **wrong** sentences. Currently only 5% of sentences show mistakes. A good benchmark needs roughly equal numbers of correct and wrong examples.

---

## For Developers

### Local setup

```bash
cd Tamil_Nadai/workbench_v2
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Visit http://localhost:8000
```

Local development uses SQLite. No database setup needed.

To enable AI features, set `GEMINI_API_KEY` as an environment variable.

### Running tests

```bash
python manage.py test core
```

All 61 tests must pass before any deploy.

### Architecture

See [CLAUDE.md](CLAUDE.md) for the full architecture, deployment process, migration pattern, and design system.

Key points:
- Django 5, Tailwind via CDN, Supabase PostgreSQL in production
- Migrations are applied via Supabase MCP, then recorded as state-only Django migrations
- The design system uses a palm-leaf manuscript metaphor with semantic colour tokens

### Coding standards

- Test every new view or model change
- Test locally with `runserver` before deploying
- Prototype UI changes in Stitch before coding templates
- Never deploy more than twice per feature
- Delete replaced code immediately — don't leave dead code

### Deployment

Only project admins deploy. See [CLAUDE.md](CLAUDE.md) for the deploy command and Cloud Run configuration.

---

## Code of Conduct

Be respectful. This is a collaborative project for Tamil language preservation. Disagreements about grammar are welcome — that's the whole point. Personal attacks are not.

## Questions?

Open a discussion on any rule page, or email tamiliam@gmail.com.
