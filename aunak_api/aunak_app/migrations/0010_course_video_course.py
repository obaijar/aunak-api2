# Generated by Django 5.0.6 on 2024-07-16 06:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aunak_app", "0009_teacher_alter_video_teacher"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(default="default", max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name="video",
            name="course",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="videos",
                to="aunak_app.course",
            ),
            preserve_default=False,
        ),
    ]
