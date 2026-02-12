"""Add EvalRun and EvalResult models. SQL already applied via Supabase."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0004_sentence_created_by"),
    ]

    operations = [
        migrations.CreateModel(
            name="EvalRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("model_name", models.CharField(choices=[("gemini-2.0-flash", "Gemini 2.0 Flash"), ("claude-sonnet-4-5", "Claude Sonnet 4.5"), ("gpt-4o", "GPT-4o")], max_length=50)),
                ("category_filter", models.CharField(blank=True, default="", max_length=100)),
                ("status_filter", models.CharField(choices=[("all", "All Sentences"), ("accepted", "Accepted Only")], default="all", max_length=20)),
                ("total_sentences", models.IntegerField(default=0)),
                ("detection_rate", models.FloatField(blank=True, null=True)),
                ("correction_accuracy", models.FloatField(blank=True, null=True)),
                ("false_positive_rate", models.FloatField(blank=True, null=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("run_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="eval_runs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="EvalResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("model_response", models.TextField(blank=True, default="")),
                ("outcome", models.CharField(choices=[("true_positive", "True Positive"), ("partial", "Partial"), ("false_negative", "False Negative"), ("true_negative", "True Negative"), ("false_positive", "False Positive"), ("error", "Error")], max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("eval_run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="core.evalrun")),
                ("sentence", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="eval_results", to="core.sentence")),
            ],
            options={
                "ordering": ["sentence__sentence_id"],
            },
        ),
    ]
