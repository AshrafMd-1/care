# Generated by Django 2.2.11 on 2021-04-26 18:32

import care.facility.models.mixins.permissions.facility
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('facility', '0221_auto_20210426_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilityInventoryBurnRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('burn_rate', models.FloatField(default=0)),
                ('current_stock', models.FloatField(default=0)),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facility.Facility')),
                ('item', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='facility.FacilityInventoryItem')),
            ],
            bases=(models.Model, care.facility.models.mixins.permissions.facility.FacilityRelatedPermissionMixin),
        ),
        migrations.AddIndex(
            model_name='facilityinventoryburnrate',
            index=models.Index(fields=['facility', 'item'], name='facility_fa_facilit_e2046a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='facilityinventoryburnrate',
            unique_together={('facility', 'item')},
        ),
    ]
