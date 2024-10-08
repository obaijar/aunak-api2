# Generated by Django 5.0.6 on 2024-07-21 07:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aunak_app", "0016_grade_subject_teacher_grades_teacher_subjects"),
    ]

    operations = [
        migrations.AlterField(
            model_name="grade",
            name="level",
            field=models.CharField(
                choices=[
                    ("9", "9th Grade"),
                    ("12", "12th Grade 3lme"),
                    ("13", "12th Grade adabe"),
                ],
                default="9",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="subject",
            name="name",
            field=models.CharField(
                choices=[
                    ("physics", "Physics"),
                    ("math", "Math"),
                    ("arabic", "Arabic"),
                    ("Philosophy", "Philosophy"),
                    ("Social Studies", "Social Studies"),
                ],
                default="physics",
                max_length=100,
            ),
        ),
    ]
