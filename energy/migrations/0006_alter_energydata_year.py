# Generated by Django 3.2.25 on 2025-04-21 22:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy', '0005_auto_20250421_1808'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energydata',
            name='year',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1985), django.core.validators.MaxValueValidator(2020)], verbose_name='Year'),
        ),
    ]
