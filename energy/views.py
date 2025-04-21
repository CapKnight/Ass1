from django.shortcuts import render, get_object_or_404
from .models import Country
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import logging

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    try:
        # Get filter parameters
        selected_region = request.GET.get('region')
        selected_income = request.GET.get('income_group')

        # Base queryset with select_related for performance
        countries = Country.objects.select_related().all().order_by('name')

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
            try:
                plt.figure(figsize=(12, 6))
                top_countries = countries.order_by('-renewable_share')[:10]
                country_names = [c.name for c in top_countries]
                renewable_shares = [c.renewable_share for c in top_countries]

                plt.barh(country_names, renewable_shares, color='#4CAF50')
                plt.xlabel('Renewable Energy Share (%)')
                plt.title('Top Renewable Energy Countries (2015)')
                plt.tight_layout()

                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close()
            except Exception as e:
                logger.error(f"Error generating index chart: {e}")
                graphic = None

        context = {
            'countries': page_obj.object_list,
            'regions': regions,
            'income_levels': income_levels,
            'graphic': graphic,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'current_region': selected_region,
            'current_income': selected_income,
            'no_data_message': 'No countries match the selected filters.' if not countries.exists() else None,
        }
        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Error in index view: {e}")
        return render(request, 'index.html', {'error': 'An error occurred while loading the page.'})

def country_detail(request, pk):
    try:
        country = get_object_or_404(Country, pk=pk)
        datapoints = country.energydata_set.all().order_by('year')

        # Generate chart
        chart_url = None
        if datapoints.exists():
            try:
                plt.figure(figsize=(10, 6))
                years = [dp.year for dp in datapoints]
                values = [dp.renewable_share for dp in datapoints]
                plt.plot(years, values, marker='o', color='#4CAF50')
                plt.title(f'Renewable Energy Trend for {country.name}')
                plt.xlabel('Year')
                plt.ylabel('Renewable Share (%)')
                plt.grid(True)
                plt.tight_layout()

                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                chart_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close()
            except Exception as e:
                logger.error(f"Error generating chart for {country.name}: {e}")
                chart_url = None

        context = {
            'country': country,
            'chart_url': chart_url,
            'error': None if datapoints.exists() else 'No data points available.',
        }
        return render(request, 'country_detail.html', context)
    except Exception as e:
        logger.error(f"Error in country_detail view: {e}")
        return render(request, 'country_detail.html', {'error': 'An error occurred while loading the country data.'})