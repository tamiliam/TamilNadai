# Tamil Nadai Workbench (தமிழ் நடை)

A collaborative workbench for Tamil language experts to review, validate, and benchmark Tamil writing convention rules — based on the **Tamil Virtual University Style Guide** (Book 169, tamilvu.org).

**Live:** [tamilnadai-90344691621.asia-southeast1.run.app](https://tamilnadai-90344691621.asia-southeast1.run.app)

## What it does

Tamil Nadai lets linguists:

- **Browse 204 grammar rules** across three categories: word joining, individual word conventions, and sandhi (vallinam doubling)
- **Add example sentences** (correct and wrong) for each rule, with AI-assisted generation via Gemini
- **Review sentences** through a two-reviewer workflow (pending → review_1_done → accepted/rejected)
- **Discuss rules** via threaded comments
- **Evaluate LLMs** against the dataset — test how well Gemini, Claude, or GPT understand Tamil grammar
- **Export the dataset** as CSV or JSON for research use

## Tech stack

| Component | Technology |
|-----------|-----------|
| Framework | Django 5, Python 3.11 |
| Database | Supabase PostgreSQL (prod), SQLite (dev) |
| CSS | Tailwind via CDN |
| Hosting | Google Cloud Run (asia-southeast1) |
| Static files | WhiteNoise |
| AI | Google Gemini 2.0 Flash |

## Local development

```bash
# Clone and set up
cd Tamil_Nadai/workbench_v2
pip install -r requirements.txt

# Run locally (uses SQLite)
python manage.py migrate
python manage.py runserver
# Visit http://localhost:8000
```

To enable AI features locally, set the `GEMINI_API_KEY` environment variable.

## Roles

| Role | Access |
|------|--------|
| Admin | Full control: rules, sentences, members, AI generation |
| Reviewer | Accept/reject sentences, propose sentences, discuss |
| Member | Propose sentences, discuss |

New members join via invitation (token-based, 7-day expiry).

## Deployment

Deployed to Cloud Run. Environment variables are set on the service (never in code):

```bash
gcloud run deploy tamilnadai \
  --source . --region asia-southeast1 --platform managed \
  --allow-unauthenticated --port 8080 --memory 512Mi \
  --no-cpu-throttling --min-instances 0 --max-instances 2
```

See [CLAUDE.md](CLAUDE.md) for detailed deployment notes, migration patterns, and architecture.

## Dataset

The workbench produces a benchmarking dataset for evaluating LLMs on Tamil grammar. See [hf_dataset/README.md](hf_dataset/README.md) for the dataset card.

## Licence

Code: MIT. Dataset: CC BY-SA 4.0. Grammar rules: Tamil Virtual University.

## Support

[Ko-fi](https://ko-fi.com/elanjelian) — help cover hosting and API costs.
