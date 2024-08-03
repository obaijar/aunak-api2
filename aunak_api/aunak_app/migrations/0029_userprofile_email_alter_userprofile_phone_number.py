# Generated by Django 5.0.6 on 2024-08-03 08:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aunak_app", "0028_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="phone_number",
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
