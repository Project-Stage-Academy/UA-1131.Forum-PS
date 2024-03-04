from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import Company


class TestCompanyFilter(APITestCase):
    """
    Test cases for filtering companies based on brand and address.

    Methods:
    - test_get_companies_filtered_by_brand: Test filtering companies by brand.
    - test_get_companies_filtered_by_address: Test filtering companies by address.
    """

    def setUp(self):
        # Create test companies with different brands and addresses
        self.company_kyiv = Company.objects.create(brand="Kyivbud", address="Kyiv")
        self.company_dnipro = Company.objects.create(brand="Dniprotrans", address="Dnipro")
        self.company_charkiv = Company.objects.create(brand="Charkivmarket", address="Charkiv")

    def test_get_companies_filtered_by_brand(self):
        """
        Test filtering companies by brand.
        """
        # Send a GET request to filter companies by brand
        response = self.client.get(path="/search/?brand=Kyivbud")

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains only the company with the specified brand
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['brand'], "Kyivbud")

    def test_get_companies_filtered_by_address(self):
        """
        Test filtering companies by address.
        """
        # Send a GET request to filter companies by address
        response = self.client.get(path="/search/?address=Dnipro")

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains only the company with the specified address
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['address'], "Dnipro")

