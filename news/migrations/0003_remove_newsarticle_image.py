# Generated by Django 5.2 on 2025-04-18 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0002_newsarticle_view_count"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="newsarticle",
            name="image",
        ),
    ]
