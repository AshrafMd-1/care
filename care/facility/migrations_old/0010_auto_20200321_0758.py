# Generated by Django 2.2.11 on 2020-03-21 07:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("facility", "0009_auto_20200320_1850"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hospitaldoctors",
            name="area",
            field=models.IntegerField(
                choices=[
                    (1, "General Medicine"),
                    (2, "Pulmonology"),
                    (3, "Critical Care"),
                    (4, "Paediatrics"),
                ]
            ),
        ),
    ]