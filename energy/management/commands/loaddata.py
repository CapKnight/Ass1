from django.core.management.base import BaseCommand
from energy.models import Country, EnergyData
import csv

class Command(BaseCommand):
    help = 'Load renewable energy data from CSV'

    def handle(self, *args, **options):
        with open('energy_data.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                country, _ = Country.objects.get_or_create(
                    name=row['country'],
                    code=row['code']
                )
                EnergyData.objects.create(
                    country=country,
                    year=row['year'],
                    renewable_pct=row['percentage']
                )
        self.stdout.write(self.style.SUCCESS('数据加载成功'))
