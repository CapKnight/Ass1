from django.test import TestCase, Client
from django.urls import reverse
from energy.models import Country, EnergyData

class EnergyModelsTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name="Test Country",
            code="TST",
            type="Country",
            region="Test Region",
            income_group="High income",
            renewable_share=50.0
        )
        self.energy_data = EnergyData.objects.create(
            country=self.country,
            year=2020,
            renewable_share=50.0
        )

    def test_country_str(self):
        self.assertEqual(str(self.country), "Test Country")

    def test_energy_data_str(self):
        self.assertEqual(str(self.energy_data), "Test Country - 2020")

    def test_unique_energy_data(self):
        with self.assertRaises(Exception):
            EnergyData.objects.create(
                country=self.country,
                year=2020,
                renewable_share=60.0
            )

class EnergyViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(
            name="Test Country",
            code="TST",
            type="Country",
            region="Test Region",
            income_group="High income",
            renewable_share=50.0
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Country")

    def test_country_detail_view(self):
        response = self.client.get(reverse('country_detail', args=[self.country.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Country")