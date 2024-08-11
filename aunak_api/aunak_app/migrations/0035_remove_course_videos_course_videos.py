# Generated by Django 5.0.6 on 2024-08-11 07:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aunak_app", "0034_course_price"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="videos",
        ),
        migrations.AddField(
            model_name="course",
            name="videos",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="aunak_app.video",
            ),
            preserve_default=False,
        ),
    ]
