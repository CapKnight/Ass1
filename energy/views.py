from django.shortcuts import render
from .models import Country

def index(request):
    countries = Country.objects.all()
    context = {
        'countries': countries,
        'regions': ['Asia', 'Europe', 'Africa', 'Americas'],
        'income_levels': ['High', 'Medium', 'Low'],
    }
    return render(request, 'index.html', context) 