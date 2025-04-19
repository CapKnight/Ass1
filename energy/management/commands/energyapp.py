import os
from django.core.management.base import BaseCommand
from django.conf import settings
from openpyxl import load_workbook
from tqdm import tqdm
from energy.models import Country, EnergyData

class Command(BaseCommand):
    help = 'Load renewable energy data from Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='energy/data/database.xlsx',
            help='Path to Excel file (relative to project root)'
        )

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, options['file'])
        
        try:
            wb = load_workbook(filename=file_path, read_only=True)
            sheet = wb['Data']
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return
        except KeyError:
            self.stderr.write(self.style.ERROR("Worksheet 'Data' not found"))
            return

        headers = [cell.value for cell in sheet[4]]
        required_columns = ['Country Name', 'Country Code', 'Type', 'Region', 'IncomeGroup', '2015']

        missing = [col for col in required_columns if col not in headers]
        if missing:
            self.stderr.write(self.style.ERROR(f"Missing required columns: {missing}"))
            return

        Country.objects.all().delete()
        EnergyData.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared existing data"))

        success_count = 0
        error_count = 0
        
        # Read rows starting from forth row (data rows)
        rows = list(sheet.iter_rows(min_row=5, values_only=True))
        
        for row in tqdm(rows, desc="Importing data"):
            try:
                if row[headers.index('Type')] != 'Country':
                    continue

                country = Country.objects.create(
                    name=row[headers.index('Country Name')] or 'Unknown',
                    code=row[headers.index('Country Code')] or None,
                    type=row[headers.index('Type')] or 'Unknown',
                    region=row[headers.index('Region')] or 'Unknown',
                    income_group=row[headers.index('IncomeGroup')] or 'Unknown',
                    renewable_share=float(row[headers.index('2015')] or 0.0)
                )

                energy_data = []
                for year in range(2010, 2016):
                    col_name = str(year)
                    if col_name in headers:
                        value = row[headers.index(col_name)]
                        try:
                            value = float(value) if value is not None else 0.0
                        except (ValueError, TypeError):
                            value = 0.0
                        energy_data.append(
                            EnergyData(
                                country=country,
                                year=year,
                                renewable_share=value
                            )
                        )
                
                EnergyData.objects.bulk_create(energy_data)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                self.stderr.write(f"Error in row {row[0]}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(
            f"Import completed! Success: {success_count}, Failed: {error_count}\n"
            f"Total countries: {Country.objects.count()}\n"
            f"Total energy records: {EnergyData.objects.count()}"
        ))