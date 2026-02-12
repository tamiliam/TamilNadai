"""State-only migration for membership module.

Tables already created via Supabase MCP SQL migration.
This migration tells Django the models exist.
"""

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MemberProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("admin", "Admin"), ("reviewer", "Reviewer"), ("member", "Member")], default="member", max_length=20)),
                ("affiliation", models.CharField(blank=True, default="", max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "core_memberprofile",
            },
        ),
        migrations.CreateModel(
            name="Invitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("role", models.CharField(choices=[("admin", "Admin"), ("reviewer", "Reviewer"), ("member", "Member")], default="member", max_length=20)),
                ("is_used", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("invited_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invitations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "core_invitation",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AlterField(
            model_name="sentence",
            name="source",
            field=models.CharField(choices=[("book", "Book"), ("ai", "AI"), ("manual", "Manual"), ("proposed", "Proposed")], default="book", max_length=10),
        ),
    ]
