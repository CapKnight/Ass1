import os
from pathlib import Path
from django.db import models
from django.core.management.base import BaseCommand, CommandError
from openpyxl import load_workbook
from energy.models import Country, EnergyData

class Command(BaseCommand):
    help = 'Load data from csv'

    def handle(self, *args, **options):
        print("hello")