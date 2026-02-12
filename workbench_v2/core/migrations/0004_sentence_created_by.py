"""Add created_by field to Sentence. SQL already applied via Supabase."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0003_memberprofile_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="sentence",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="sentences_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
