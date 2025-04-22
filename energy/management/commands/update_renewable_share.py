# 在 energy/management/commands/update_renewable_share.py 中
from django.core.management.base import BaseCommand
from energy.models import Country, EnergyData

class Command(BaseCommand):
    help = 'Update renewable_share in Country model from EnergyData for 2015'

    def handle(self, *args, **kwargs):
        for country in Country.objects.all():
            energy_data = EnergyData.objects.filter(country=country, year=2015).first()
            if energy_data:
                country.renewable_share = energy_data.renewable_share
                country.save()
                self.stdout.write(self.style.SUCCESS(f"Updated {country.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"No 2015 data for {country.name}"))