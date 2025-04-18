# Generated by Django 3.2.25 on 2025-04-18 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='income_group',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='region',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='type',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(max_length=4, unique=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
