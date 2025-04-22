from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=4, unique=True, null=True, blank=True)
    type = models.CharField(max_length=10, default='Unknown')
    region = models.CharField(max_length=50, default='Unknown')
    INCOME_GROUP_CHOICES = [
        ('High income', 'High income'),
        ('Low income', 'Low income'),
        ('Lower middle', 'Lower middle income'),
        ('Upper middle', 'Upper middle income'),
    ]
    income_group = models.CharField(
        max_length=20, choices=INCOME_GROUP_CHOICES, blank=True, null=True
    )

    renewable_share = models.FloatField(help_text="Renewable energy share in 2015 (%)")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class EnergyData(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    year = models.IntegerField()
    renewable_share = models.FloatField()

    def __str__(self):
        return f"{self.country.name} - {self.year}"

    class Meta:
        unique_together = ('country', 'year')
        ordering = ['year']