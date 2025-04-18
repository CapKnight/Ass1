from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=4, unique=True)
    type = models.CharField(max_length=10, null=True)
    region = models.CharField(max_length=20, null=True)
    income_group = models.CharField(max_length=30, null=True)

class EnergyData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    year = models.IntegerField()
    renewable_pct = models.FloatField()