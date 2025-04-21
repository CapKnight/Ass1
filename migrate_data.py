import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from energy.models import Country, EnergyData

def transfer_existing_data():
    for country in Country.objects.exclude(renewable_share__isnull=True):
        EnergyData.objects.create(
            country=country,
            year=2015,
            renewable_share=country.renewable_share
        )
    print(f"Migrated {Country.objects.count()} countries' data")

if __name__ == '__main__':
    transfer_existing_data()