# Generated by Django 3.2.25 on 2025-04-18 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy', '0002_auto_20250418_1400'),
    ]

    operations = [
        migrations.RenameField(
            model_name='energydata',
            old_name='renewable_pct',
            new_name='renewable_share',
        ),
        migrations.AddField(
            model_name='country',
            name='renewable_share',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(blank=True, max_length=4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='income_group',
            field=models.CharField(default='Unknown', max_length=30),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='region',
            field=models.CharField(default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='country',
            name='type',
            field=models.CharField(default='Unknown', max_length=10),
        ),
    ]
