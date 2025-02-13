from datetime import timezone, datetime
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings


class FareCalculationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("calculate-fare")

    def test_valid_request(self):
        response = self.client.get(
            self.url,
            {"distance": "10", "traffic_level": "high", "demand_level": "peak"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_fare", response.data)

    def test_serializer_validation(self):
        # Test invalid distance
        response = self.client.get(self.url, {"distance": "invalid"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("distance", response.data)

        # Test invalid traffic level
        response = self.client.get(
            self.url, {"distance": "10", "traffic_level": "invalid"}
        )
        self.assertIn("traffic_level", response.data)

    def test_high_traffic_multiplier(self):
        response = self.client.get(
            self.url,
            {"distance": "8", "traffic_level": "high", "demand_level": "normal"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["multipliers"]["traffic"], 1.5)

    def test_demand_surge_multiplier(self):
        response = self.client.get(
            self.url,
            {"distance": "12", "traffic_level": "normal", "demand_level": "peak"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["multipliers"]["demand"], 1.8)

    def test_combined_multipliers(self):
        response = self.client.get(
            self.url,
            {"distance": "7", "traffic_level": "high", "demand_level": "peak"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["multipliers"]["traffic"], 1.5)
        self.assertEqual(response.data["multipliers"]["demand"], 1.8)

    def test_long_distance_fare(self):
        response = self.client.get(
            self.url,
            {"distance": "20", "traffic_level": "normal", "demand_level": "normal"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["multipliers"]["traffic"], 1.0)
        self.assertEqual(response.data["multipliers"]["demand"], 1.0)

    def test_missing_distance(self):
        response = self.client.get(
            self.url, {"traffic_level": "normal", "demand_level": "normal"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("distance", response.data)

    def test_negative_distance(self):
        response = self.client.get(
            self.url,
            {"distance": "-5", "traffic_level": "normal", "demand_level": "normal"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("distance", response.data)

    def test_invalid_traffic_level(self):
        response = self.client.get(
            self.url,
            {"distance": "10", "traffic_level": "invalid", "demand_level": "normal"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("traffic_level", response.data)

    def test_invalid_demand_level(self):
        response = self.client.get(
            self.url,
            {"distance": "10", "traffic_level": "normal", "demand_level": "invalid"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("demand_level", response.data)

    def test_min_distance(self):
        response = self.client.get(
            self.url,
            {"distance": "0.1", "traffic_level": "low", "demand_level": "normal"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance_fare"], 0.1 * settings.PER_KM_RATE)

    def test_max_distance(self):
        response = self.client.get(
            self.url,
            {"distance": "100", "traffic_level": "normal", "demand_level": "normal"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance_fare"], 100 * settings.PER_KM_RATE)

    @patch("pricing.helpers.timezone.now")
    def test_no_multipliers(self, mock_now):
        # Mock time to a non-peak hour (e.g., 2:00 AM on a Monday)
        mock_now.return_value = datetime(2025, 2, 10, 2, 0, 0, tzinfo=timezone.utc)

        response = self.client.get(
            self.url,
            {"distance": "10", "traffic_level": "low", "demand_level": "normal"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["multipliers"]["traffic"], 1.0)
        self.assertEqual(response.data["multipliers"]["demand"], 1.0)
        self.assertEqual(response.data["multipliers"]["time"], 1.0)
