# Generated by Django 5.2 on 2025-04-19 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_course_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
