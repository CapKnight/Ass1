from django.shortcuts import render
from .models import Country
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def index(request):
    # Get filter parameters
    selected_region = request.GET.get('region')
    selected_income = request.GET.get('income_group')

    # Base queryset
    countries = Country.objects.all().order_by('name')

    # Apply filters
    if selected_region and selected_region != 'Unknown':
        countries = countries.filter(region=selected_region)
    if selected_income and selected_income != 'Unknown':
        countries = countries.filter(income_group=selected_income)

    # Pagination
    paginator = Paginator(countries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options from database
    regions = Country.objects.exclude(region='Unknown').values_list(
        'region', flat=True).distinct().order_by('region')
    income_levels = Country.objects.exclude(income_group='Unknown').values_list(
        'income_group', flat=True).distinct().order_by('income_group')

    # Generate chart
    graphic = None
    if countries.exists():
        plt.figure(figsize=(12, 6))
        top_countries = countries.order_by('-renewable_share')[:10]
        country_names = [c.name for c in top_countries]
        renewable_shares = [c.renewable_share for c in top_countries]

        plt.barh(country_names, renewable_shares, color='#4CAF50')
        plt.xlabel('Renewable Energy Share (%)')
        plt.title('Top Renewable Energy Countries')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

    context = {
        'countries': page_obj.object_list,
        'regions': regions,
        'income_levels': income_levels,
        'graphic': graphic,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'current_region': selected_region,
        'current_income': selected_income,
    }
    return render(request, 'index.html', context)