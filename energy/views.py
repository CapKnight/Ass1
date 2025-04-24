from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Country, EnergyData
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging
import folium
import geopandas as gpd
import os
from django.conf import settings
import pandas as pd
from django.db.models import Prefetch
import random
from django.template.defaulttags import register

logger = logging.getLogger(__name__)
YEARS_RANGE = range(1990, 2016)

def index(request):
    try:
        region = request.GET.get('region')
        income_group = request.GET.get('income_group')

        base_query = Country.objects.prefetch_related('energydata_set').order_by('name')

        filtered_countries = base_query
        if region and region != 'Unknown':
            filtered_countries = filtered_countries.filter(region=region)
        if income_group and income_group != 'Unknown':
            filtered_countries = filtered_countries.filter(income_group=income_group)

        paginator = Paginator(
            filtered_countries.values_list(
                'id', 'name', 'code', 'region', 'income_group'
            ), 
            20
        )
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        country_data = []
        for country_tuple in page_obj.object_list:
            country = Country.objects.get(id=country_tuple[0])
            energy_data = {str(ed.year): ed.renewable_share 
                          for ed in country.energydata_set.all()}
            renewable_share_2015 = energy_data.get("2015", None)
            income_group_display = dict(Country.INCOME_GROUP_CHOICES).get(country_tuple[4], 'Unknown')
            data = {
                'id': country_tuple[0],
                'name': country_tuple[1],
                'code': country_tuple[2],
                'region': country_tuple[3],
                'income_group': income_group_display,
                'energy': energy_data,
                'renewable_share_2015': renewable_share_2015
            }
            country_data.append(data)

        regions = Country.objects.exclude(region='Unknown') \
            .values_list('region', flat=True) \
            .distinct() \
            .order_by('region')
        income_groups = [choice[1] for choice in Country.INCOME_GROUP_CHOICES]

        graphic = generate_chart(filtered_countries)

        context = {
            'all_countries': base_query,
            'country_data': country_data,
            'years': YEARS_RANGE,
            'regions': regions,
            'income_groups': income_groups,
            'current_region': region,
            'current_income': income_group,
            'graphic': graphic,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        }
        return render(request, 'energy/index.html', context)
    except Exception as e:
        logger.error(f"Error: {e}")
        empty_paginator = Paginator([], 1)
        page_obj = empty_paginator.page(1)
        return render(request, 'energy/index.html', {
            'error': str(e),
            'page_obj': page_obj,
            'country_data': [],
            'years': YEARS_RANGE,
            'regions': [],
            'income_groups': [],
            'all_countries': Country.objects.none(),
            'current_region': None,
            'current_income': None,
            'graphic': None
        })

def generate_country_chart(energy_data):
    try:
        all_years = [d['year'] for d in energy_data]
        all_values = [d['renewable_share'] for d in energy_data]
        plt.figure(figsize=(12, 6))
        plt.plot(all_years, all_values, 
                 marker='o', color='#2e7d32', linewidth=2,
                 markersize=8, linestyle='-', markeredgecolor='#2e7d32')
        plt.xticks(range(1990, 2016), rotation=45)
        plt.xlim(1989.5, 2015.5)
        plt.ylim(0, 100)
        plt.title("Renewable Energy Trend (1990-2015)")
        plt.xlabel('Year')
        plt.ylabel('Renewable Share (%)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        chart_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        return chart_url
    except Exception as e:
        logger.error(f"Chart Generation Error: {str(e)}")
        return None

def generate_chart(queryset):
    try:
        plt.figure(figsize=(12, 6))
        valid_countries = [c for c in queryset[:10] if c.energydata_set.exists()]
        if not valid_countries:
            return None
        countries_data = []
        renewable_share = []
        for country in valid_countries:
            latest_data = country.energydata_set.order_by('-year').first()
            if latest_data:
                countries_data.append(f"{country.name}\n({country.code})")
                renewable_share.append(latest_data.renewable_share)
        plt.barh(countries_data, renewable_share, color='#2e7d32')
        plt.xlabel('Latest Renewable Share (%)')
        plt.title('Top Countries by Renewable Energy')
        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        return graphic
    except Exception as e:
        logger.error(f"Chart error: {e}")
        return None

def country_detail(request, pk):
    country = get_object_or_404(
        Country.objects.prefetch_related(
            Prefetch(
                'energydata_set',
                queryset=EnergyData.objects.filter(year__range=(1990, 2015)).order_by('year'),
                to_attr='filtered_energy'
            )
        ),
        pk=pk
    )
    full_energy_data = [
        {
            'year': year,
            'renewable_share': next(
                (ed.renewable_share for ed in country.filtered_energy if ed.year == year),
                None
            ),
        }
        for year in range(1990, 2016)
    ]
    chart_url = generate_country_chart(full_energy_data)
    context = {
        'country': country,
        'energy_data': full_energy_data,
        'chart_url': chart_url,
    }
    return render(request, 'energy/country_detail.html', context)

def map_view(request):
    try:
        m = folium.Map(
            location=[20, 0], zoom_start=2, tiles="cartodbpositron",
            max_bounds=True, min_zoom=2, max_zoom=10,
        )
        geojson_path = os.path.join(settings.STATICFILES_DIRS[0], 'geojson', 'ne_110m_admin_0_countries.geojson')
        logger.info(f"GeoJSON path: {geojson_path}")
        if not os.path.exists(geojson_path):
            logger.error(f"GeoJSON file not found at {geojson_path}")
            return render(request, 'energy/maps.html', {'error': 'Map data not found.'})
        gdf = gpd.read_file(geojson_path)
        countries = Country.objects.all()
        energy_data = EnergyData.objects.filter(year=2015).select_related('country')
        data = pd.DataFrame([
            {
                'name': ed.country.name,
                'renewable_share': ed.renewable_share,
                'code': ed.country.code,
            }
            for ed in energy_data
        ])
        gdf = gdf.merge(data, how='left', left_on='SOV_A3', right_on='code')
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
        folium.LayerControl().add_to(m)
        map_html = m._repr_html_()
        return render(request, 'energy/maps.html', {
            'map_html': map_html,
            'error': None
        })
    except Exception as e:
        logger.error(f"Error generating map: {e}")
        return render(request, 'energy/maps.html', {'error': str(e)})

@register.filter
def dict_key(d, key):
    return d.get(key)

def compare_countries(request):
    try:
        selected_ids = [cid for cid in request.GET.getlist('countries') if cid.isdigit()]
        valid_countries = Country.objects.filter(id__in=selected_ids)
        sorted_countries = valid_countries.order_by('name')

        context = {
            'countries': Country.objects.all().order_by('name'),
            'selected_countries': selected_ids,
            'selected_countries_qs': sorted_countries,
            'years': [],
            'datasets': [],
            'table_data': [],
            'error': None
        }

        if sorted_countries.exists():
            years = list(EnergyData.objects.filter(
                country__in=sorted_countries
            ).values_list('year', flat=True).distinct().order_by('year'))
            
            if not years:
                years = list(range(1990, 2016))
            
            context['years'] = years

            all_energy_data = {
                (data.country_id, data.year): data.renewable_share
                for data in EnergyData.objects.filter(
                    country__in=sorted_countries,
                    year__in=years
                )
            }

            datasets = []
            for country in sorted_countries:
                data_points = []
                for year in years:
                    value = all_energy_data.get((country.id, year))
                    data_points.append(float(value) if value is not None else None)
                
                datasets.append({
                    'label': country.name,
                    'data': data_points,
                    'borderColor': f'hsl({random.randint(0, 360)}, 70%, 50%)'
                })
            context['datasets'] = datasets

            table_data = []
            for year in years:
                row = {'year': year, 'countries': {}}
                for country in sorted_countries:
                    value = all_energy_data.get((country.id, year))
                    row['countries'][country.id] = {'renewable_share': value}
                table_data.append(row)
            context['table_data'] = table_data

        return render(request, 'energy/compare.html', context)

    except Exception as e:
        logger.error(f"Comparison error: {str(e)}", exc_info=True)
        context['error'] = "Data loading failed"
        return render(request, 'energy/compare.html', context)