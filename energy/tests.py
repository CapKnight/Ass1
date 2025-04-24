from django.test import TestCase, Client
from django.urls import reverse
from energy.models import Country, EnergyData
from django.core.paginator import Paginator
from unittest.mock import patch, MagicMock
import base64
from io import BytesIO

class CountryModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name="Test Country",
            code="TC",
            type="Test Type",
            region="Test Region",
            income_group="High income",
            renewable_share=50.0
        )

    def test_country_creation(self):
        self.assertEqual(self.country.name, "Test Country")
        self.assertEqual(self.country.code, "TC")
        self.assertEqual(self.country.type, "Test Type")
        self.assertEqual(self.country.region, "Test Region")
        self.assertEqual(self.country.income_group, "High income")
        self.assertEqual(self.country.renewable_share, 50.0)

    def test_country_string_representation(self):
        self.assertEqual(str(self.country), "Test Country")

    def test_country_ordering(self):
        country2 = Country.objects.create(name="Another Country", code="AC")
        countries = Country.objects.all()
        self.assertEqual(countries[0].name, "Another Country")
        self.assertEqual(countries[1].name, "Test Country")

    def test_country_unique_name(self):
        with self.assertRaises(Exception):
            Country.objects.create(name="Test Country", code="TC2")

class EnergyDataModelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.energy_data = EnergyData.objects.create(
            country=self.country,
            year=2015,
            renewable_share=60.0
        )

    def test_energy_data_creation(self):
        self.assertEqual(self.energy_data.country, self.country)
        self.assertEqual(self.energy_data.year, 2015)
        self.assertEqual(self.energy_data.renewable_share, 60.0)

    def test_energy_data_string_representation(self):
        self.assertEqual(str(self.energy_data), "Test Country - 2015")

    def test_energy_data_unique_together(self):
        with self.assertRaises(Exception):
            EnergyData.objects.create(country=self.country, year=2015, renewable_share=70.0)

    def test_energy_data_ordering(self):
        energy_data2 = EnergyData.objects.create(country=self.country, year=2014, renewable_share=55.0)
        energy_data = EnergyData.objects.all()
        self.assertEqual(energy_data[0].year, 2014)
        self.assertEqual(energy_data[1].year, 2015)

class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(
            name="Test Country",
            code="TC",
            region="Test Region",
            income_group="High income",
            renewable_share=50.0
        )
        EnergyData.objects.create(country=self.country, year=2015, renewable_share=60.0)

    @patch('energy.views.plt')
    def test_index_view(self, mock_plt):
        # Mock the chart generation to avoid matplotlib issues
        mock_savefig = MagicMock()
        mock_savefig.return_value = None
        mock_plt.savefig = mock_savefig
        mock_buffer = MagicMock()
        mock_buffer.getvalue.return_value = b"mocked_image_data"
        mock_plt.gcf.return_value.canvas.buffer = mock_buffer
        response = self.client.get(reverse('energy:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'energy/index.html')
        self.assertIn('country_data', response.context)
        self.assertIn('page_obj', response.context)
        self.assertIn('graphic', response.context)
        self.assertEqual(len(response.context['country_data']), 1)
        self.assertEqual(response.context['country_data'][0]['name'], "Test Country")

    def test_index_view_with_filters(self):
        response = self.client.get(reverse('energy:index'), {'region': 'Test Region'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['country_data']), 1)
        self.assertEqual(response.context['country_data'][0]['region'], "Test Region")

        response = self.client.get(reverse('energy:index'), {'region': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['country_data']), 0)

    def test_index_view_pagination(self):
        # Create more countries to test pagination
        for i in range(25):
            Country.objects.create(name=f"Country {i}", code=f"C{i}")
        response = self.client.get(reverse('energy:index'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['country_data']), 20)  # Default per page

    @patch('energy.views.plt')
    def test_index_view_error_handling(self, mock_plt):
        # Simulate an error in chart generation
        mock_savefig = MagicMock()
        mock_savefig.side_effect = Exception("Chart error")
        mock_plt.savefig = mock_savefig
        response = self.client.get(reverse('energy:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['graphic'], None)  # 验证 graphic 为 None

class CountryDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(
            name="Test Country",
            code="TC",
            region="Test Region",
            income_group="High income"
        )
        EnergyData.objects.create(country=self.country, year=2015, renewable_share=60.0)

    @patch('energy.views.plt')
    def test_country_detail_view(self, mock_plt):
        mock_savefig = MagicMock()
        mock_savefig.return_value = None
        mock_plt.savefig = mock_savefig
        mock_buffer = MagicMock()
        mock_buffer.getvalue.return_value = b"mocked_image_data"
        mock_plt.gcf.return_value.canvas.buffer = mock_buffer
        response = self.client.get(reverse('energy:country_detail', args=[self.country.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'energy/country_detail.html')
        self.assertIn('country', response.context)
        self.assertIn('energy_data', response.context)
        self.assertIn('chart_url', response.context)
        self.assertEqual(response.context['country'].name, "Test Country")

    def test_country_detail_view_404(self):
        response = self.client.get(reverse('energy:country_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

class MapViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(name="Test Country", code="TC")
        EnergyData.objects.create(country=self.country, year=2015, renewable_share=60.0)

    @patch('energy.views.folium.GeoJson')
    @patch('energy.views.folium.Choropleth')
    @patch('energy.views.gpd.read_file')
    @patch('energy.views.folium.Map')
    def test_map_view(self, mock_map, mock_read_file, mock_choropleth, mock_geojson):
        # 模拟 folium.Map 的返回值
        mock_map_instance = MagicMock()
        mock_map_instance._repr_html_.return_value = "<div>Mock Map</div>"
        mock_map.return_value = mock_map_instance

        # 模拟 geopandas 的 GeoDataFrame
        mock_gdf = MagicMock()
        mock_merged_gdf = MagicMock()
        mock_gdf.merge.return_value = mock_merged_gdf
        mock_read_file.return_value = mock_gdf

        # 模拟 folium.Choropleth 和 folium.GeoJson
        mock_choropleth.return_value = MagicMock()
        mock_geojson.return_value = MagicMock()

        # 模拟 pandas DataFrame
        with patch('energy.views.pd.DataFrame', return_value=MagicMock()):
            response = self.client.get(reverse('energy:map'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'energy/maps.html')
            self.assertIn('map_html', response.context)
            self.assertEqual(response.context['map_html'], "<div>Mock Map</div>")

    @patch('energy.views.os.path.exists')
    def test_map_view_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        response = self.client.get(reverse('energy:map'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], "Map data not found.")

class CompareCountriesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country1 = Country.objects.create(name="Country 1", code="C1")
        self.country2 = Country.objects.create(name="Country 2", code="C2")
        EnergyData.objects.create(country=self.country1, year=2015, renewable_share=60.0)
        EnergyData.objects.create(country=self.country2, year=2015, renewable_share=50.0)

    def test_compare_countries_view_no_selection(self):
        response = self.client.get(reverse('energy:compare'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'energy/compare.html')
        self.assertIn('countries', response.context)
        self.assertIn('selected_countries', response.context)
        self.assertEqual(len(response.context['selected_countries']), 0)
        self.assertEqual(len(response.context['datasets']), 0)

    def test_compare_countries_view_with_selection(self):
        response = self.client.get(reverse('energy:compare'), {
            'countries': [str(self.country1.id), str(self.country2.id)]
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('selected_countries_qs', response.context)
        self.assertIn('datasets', response.context)
        self.assertEqual(len(response.context['selected_countries_qs']), 2)
        self.assertEqual(len(response.context['datasets']), 2)
        self.assertEqual(response.context['datasets'][0]['label'], "Country 1")

    def test_compare_countries_view_error_handling(self):
        # Simulate an error by mocking EnergyData query to fail
        with patch('energy.views.EnergyData.objects.filter') as mock_filter:
            mock_filter.side_effect = Exception("Database error")
            response = self.client.get(reverse('energy:compare'), {
                'countries': [str(self.country1.id)]
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn('error', response.context)
            self.assertEqual(response.context['error'], "Data loading failed")