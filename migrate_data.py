import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from dataapp.models import DataPoint
from energy.models import Country, EnergyData

def migrate_data():
    for dp in DataPoint.objects.all():
        country, created = Country.objects.get_or_create(
            name=dp.country.name,
            defaults={
                'region': 'Unknown',
                'income_group': 'Unknown',
                'renewable_share': dp.value,
                'code': None,
                'type': 'Unknown'
            }
        )
        EnergyData.objects.create(
            country=country,
            year=dp.year,
            renewable_share=dp.value
        )
    print(f"Migrated {DataPoint.objects.count()} data points.")

if __name__ == '__main__':
    migrate_data()