from django.shortcuts import render, get_object_or_404
from .models import Country
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import logging
import folium
import geopandas as gpd
import os
from django.conf import settings
import pandas as pd

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

def map_view(request):
    try:
        # Initialize Folium map centered on the world
        m = folium.Map(
            location=[20, 0],
            zoom_start=2,
            tiles="cartodbpositron",
            max_bounds=True,
            min_zoom=2,
            max_zoom=10,
        )

        # Load GeoJSON file
        geojson_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'geojson', 'ne_110m_admin_0_countries.geojson')
        if not os.path.exists(geojson_path):
            logger.error(f"GeoJSON file not found at {geojson_path}")
            return render(request, 'map.html', {'error': 'Map data not found.'})

        gdf = gpd.read_file(geojson_path)

        # Get country data from database (latest year, e.g., 2015)
        countries = Country.objects.all()
        energy_data = EnergyData.objects.filter(year=2015).select_related('country')

        # Create a DataFrame for merging
        data = pd.DataFrame([
            {
                'name': ed.country.name,
                'renewable_share': ed.renewable_share,
                'code': ed.country.code,
            }
            for ed in energy_data
        ])

        # Merge GeoJSON with country data
        gdf = gdf.merge(data, how='left', left_on='SOV_A3', right_on='code')

        # Add choropleth layer
        folium.Choropleth(
            geo_data=gdf,
            name='Renewable Energy',
            data=data,
            columns=['name', 'renewable_share'],
            key_on='feature.properties.NAME',
            fill_color='YlGn',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Renewable Energy Share (%)',
            nan_fill_color='gray',
            nan_fill_opacity=0.4,
        ).add_to(m)

        # Add GeoJSON layer for interactivity
        folium.GeoJson(
            gdf,
            name='Countries',
            style_function=lambda x: {
                'fillColor': '#cccccc' if pd.isna(x['properties']['renewable_share']) else None,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'renewable_share'],
                aliases=['Country:', 'Renewable Share (%):'],
                localize=True,
                sticky=True,
            ),
            popup=folium.GeoJsonPopup(
                fields=['NAME', 'renewable_share'],
                aliases=['Country:', 'Renewable Share (%):'],
                labels=True,
            ),
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Save map to HTML string
        map_html = m._repr_html_()

        context = {
            'map_html': map_html,
            'error': None,
        }
        return render(request, 'map.html', context)
    except Exception as e:
        logger.error(f"Error generating map: {e}")
        return render(request, 'map.html', {'error': 'An error occurred while generating the map.'})