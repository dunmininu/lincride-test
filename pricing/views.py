from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.core.cache import cache

from pricing.helpers import is_peak_hour
from pricing.serializers import (
    FareCalculationQuerySerializer,
    FareCalculationResponseSerializer,
)
from ride_pricing import settings


class CalculateFareView(APIView):
    """
    Calculate dynamic ride pricing based on distance, traffic,
    and demand level. the peak hours are determined
    using the time of the day and the day of
    the week. this is based on the assumption
    that peak hours are when people are either going to
    office or on their way back, or people going to have
    fun in the evening.
    Example: /api/calculate-fare/?demand_level=peak&distance=3&traffic_level=high # noqa
    """

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="distance",
                description="Ride distance in kilometers (0.1-100)",
                required=True,
                type=float,
            ),
            OpenApiParameter(
                name="traffic_level",
                description="Traffic condition level",
                required=False,
                type=str,
                enum=["low", "normal", "high"],
            ),
            OpenApiParameter(
                name="demand_level",
                description="Demand surge level",
                required=False,
                type=str,
                enum=["normal", "peak"],
            ),
        ],
        responses={200: FareCalculationResponseSerializer},
        description="Calculate fare based on distance, traffic, and demand level.",
    )
    def get(
        self,
        request,
    ):
        serializer = FareCalculationQuerySerializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)

        fare_details = self.calculate_fare(serializer.validated_data)
        return Response(fare_details)

    def calculate_fare(self, validated_data):
        cache_key = f"fare_{validated_data['distance']}_{validated_data['traffic_level']}_{validated_data['demand_level']}"
        cached_fare = cache.get(cache_key)

        if cached_fare:
            return cached_fare

        base = settings.BASE_FARE
        distance = validated_data["distance"]

        multipliers = self.get_multipliers(validated_data)

        total = (
            (base + (distance * settings.PER_KM_RATE))
            * multipliers["traffic"]
            * multipliers["demand"]
            * multipliers["time"]
        )

        data = {
            "base_fare": base,
            "distance_fare": round(distance * settings.PER_KM_RATE, 2),
            "multipliers": multipliers,
            "total_fare": round(total, 2),
        }

        cache.set(cache_key, data, timeout=300)

        serialized_data = FareCalculationResponseSerializer(data).data

        return serialized_data

    def get_multipliers(self, validated_data):
        return {
            "traffic": self.get_traffic_multiplier(validated_data["traffic_level"]),
            "demand": self.get_demand_multiplier(validated_data["demand_level"]),
            "time": self.get_time_multiplier(),
        }

    def get_time_multiplier(self):
        return 1.3 if is_peak_hour() else 1.0

    def get_traffic_multiplier(self, level):
        return {"low": 1.0, "normal": 1.0, "high": 1.5}.get(level, 1.0)

    def get_demand_multiplier(self, level):
        return {"normal": 1.0, "peak": 1.8}[level]
