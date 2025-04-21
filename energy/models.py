from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Country(models.Model):
    """
    Core country information model
    """
    
    INCOME_LEVELS = [
        ('L', 'Low income'),
        ('LM', 'Lower middle income'),
        ('UM', 'Upper middle income'), 
        ('H', 'High income'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Country Name"
    )
    
    code = models.CharField(
        max_length=4,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Country Code"
    )
    
    region = models.CharField(
        max_length=50,
        default='Unknown',
        verbose_name="Region"
    )
    
    income_group = models.CharField(
        max_length=30,
        choices=INCOME_LEVELS,
        default='Unknown',
        verbose_name="Income Group"
    )
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name
        
    def get_latest_energy_data(self):
        """Retrieve most recent energy data"""
        return self.energydata_set.order_by('-year').first()
        
    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']
        indexes = [
            models.Index(fields=['region']),
            models.Index(fields=['income_group']),
        ]


class EnergyData(models.Model):
    """
    Annual energy metrics by country
    """
    
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        verbose_name="Related Country"
    )
    
    year = models.IntegerField(
        validators=[
            MinValueValidator(1985),
            MaxValueValidator(2020)
        ],
        verbose_name="Year"
    )
    
    renewable_share = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Renewable Energy Share (%)"
    )
    
    fossil_share = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Fossil Fuel Share (%)"
    )
    
    class Meta:
        verbose_name = "Energy Data"
        verbose_name_plural = "Energy Dataset"
        ordering = ['-year']
        unique_together = [('country', 'year')]
        get_latest_by = 'year'
        
    def __str__(self):
        return f"{self.country.name} {self.year}: {self.renewable_share}% renewable"

    def clean(self):
        """Validate energy share totals"""
        if self.fossil_share and (self.renewable_share + self.fossil_share > 100):
            raise ValidationError("Total energy share cannot exceed 100%")