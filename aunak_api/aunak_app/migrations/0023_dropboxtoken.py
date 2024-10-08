# Generated by Django 5.0.6 on 2024-07-29 08:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aunak_app", "0022_remove_video_video_file_video_video_file_path"),
    ]

    operations = [
        migrations.CreateModel(
            name="DropboxToken",
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
                ("access_token", models.CharField(max_length=255)),
                (
                    "refresh_token",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("token_type", models.CharField(blank=True, max_length=50, null=True)),
                ("expires_in", models.IntegerField(blank=True, null=True)),
                ("scope", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
