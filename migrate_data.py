
import csv
import os
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Data migration commands'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command')

        # CSV import subcommand
        csv_parser = subparsers.add_parser('csv_import', help='Import data from CSV')
        csv_parser.add_argument(
            '--file',
            default='energy_data.csv',
            help='Path to CSV file (relative to project root)'
        )

        # Data transfer subcommand
        subparsers.add_parser('migrate_legacy', help='Migrate existing country data')

    def handle(self, *args, **options):
        if options['command'] == 'csv_import':
            self.handle_csv_import(options)
        elif options['command'] == 'migrate_legacy':
            self.handle_migrate_legacy()
        else:
            self.stdout.write(self.style.ERROR('Invalid command'))

    @transaction.atomic
    def handle_csv_import(self, options):
        file_path = os.path.join(settings.BASE_DIR, options['file'])
        
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        success_count = 0
        error_count = 0
        
# will handle the errors
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
                        logger.error(f"Error processing row {row}: {str(e)}")

            self.stdout.write(self.style.SUCCESS(
                f"CSV import completed! Success: {success_count}, Failed: {error_count}\n"
                f"Total countries: {Country.objects.count()}\n"
                f"Total energy records: {EnergyData.objects.count()}"
            ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading CSV file: {str(e)}"))

    @transaction.atomic
    def handle_migrate_legacy(self):
        migrated_count = 0
        for country in Country.objects.exclude(renewable_share__isnull=True):
            EnergyData.objects.create(
                country=country,
                year=2015,
                renewable_share=country.renewable_share
            )
            migrated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Legacy data migration completed!\n"
            f"Migrated {migrated_count} countries' data"
        ))