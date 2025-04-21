import os
<<<<<<< Updated upstream
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
=======
import csv
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from energy.models import Country, EnergyData

# Set up logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Migrate energy data from CSV to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='energy_data.csv',
            help='Path to CSV file (relative to project root)'
        )

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, options['file'])
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        success_count = 0
        error_count = 0

        try:
            with open(file_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        country, _ = Country.objects.get_or_create(
                            name=row['country'],
                            defaults={
                                'code': row['code'] or None,
                                'type': 'Country',
                                'region': 'Unknown',
                                'income_group': 'Unknown',
                                'renewable_share': float(row['percentage']) if row['percentage'] else 0.0
                            }
                        )
                        EnergyData.objects.get_or_create(
                            country=country,
                            year=int(row['year']),
                            renewable_share=float(row['percentage']) if row['percentage'] else 0.0
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error processing row {row}: {e}")
                        
            self.stdout.write(self.style.SUCCESS(
                f"Migration completed! Success: {success_count}, Failed: {error_count}\n"
                f"Total countries: {Country.objects.count()}\n"
                f"Total energy records: {EnergyData.objects.count()}"
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading CSV file: {e}"))
>>>>>>> Stashed changes
