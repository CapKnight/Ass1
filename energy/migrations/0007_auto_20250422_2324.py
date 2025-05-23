# Generated by Django 3.2.25 on 2025-04-22 23:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('energy', '0006_alter_energydata_year'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='energydata',
            options={'ordering': ['year']},
        ),
        migrations.RemoveIndex(
            model_name='country',
            name='energy_coun_region_e5d8c6_idx',
        ),
        migrations.RemoveIndex(
            model_name='country',
            name='energy_coun_income__9be668_idx',
        ),
        migrations.RemoveField(
            model_name='energydata',
            name='fossil_share',
        ),
        migrations.AddField(
            model_name='country',
            name='renewable_share',
            field=models.FloatField(blank=True, default=0.0, help_text='Renewable energy share in 2015 (%)', null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='type',
            field=models.CharField(default='Unknown', max_length=10),
        ),
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(blank=True, max_length=4, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='income_group',
            field=models.CharField(blank=True, choices=[('High income', 'High income'), ('Low income', 'Low income'), ('Lower middle', 'Lower middle income'), ('Upper middle', 'Upper middle income')], max_length=20, null=True),
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
            model_name='energydata',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='energy.country'),
        ),
        migrations.AlterField(
            model_name='energydata',
            name='renewable_share',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='energydata',
            name='year',
            field=models.IntegerField(),
        ),
    ]
