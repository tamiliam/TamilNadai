"""Add avatar field to MemberProfile. SQL already applied via Supabase."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_membership"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberprofile",
            name="avatar",
            field=models.TextField(blank=True, default=""),
        ),
    ]
