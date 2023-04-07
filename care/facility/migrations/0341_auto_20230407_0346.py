# Generated by Django 2.2.11 on 2023-04-06 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facility', '0340_auto_20230406_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyround',
            name='ventilator_interface',
            field=models.IntegerField(choices=[(0, 'UNKNOWN'), (5, 'INVASIVE'), (10, 'NON_INVASIVE'), (15, 'OXYGEN_SUPPORT')], default=0),
        ),
        # convert all UNKNOWN fields in db to OXYGEN_SUPPORT
        migrations.RunSQL(
            sql="UPDATE facility_dailyround SET ventilator_interface = 15 WHERE ventilator_interface = 0 AND (ventilator_oxygen_modality != 0 OR ventilator_oxygen_modality_flow_rate IS NOT NULL OR ventilator_oxygen_modality_oxygen_rate IS NOT NULL)",
            reverse_sql="UPDATE facility_dailyround SET ventilator_interface = 0 WHERE ventilator_interface = 15 AND (ventilator_oxygen_modality = 0 AND ventilator_oxygen_modality_flow_rate IS NULL AND ventilator_oxygen_modality_oxygen_rate IS NULL)",
        ),
    ]

    