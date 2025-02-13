from rest_framework import serializers


class FareCalculationQuerySerializer(serializers.Serializer):
    distance = serializers.FloatField(
        min_value=0.1, max_value=100, help_text="Ride distance in kilometers (0.1-100)"
    )
    traffic_level = serializers.ChoiceField(
        choices=["low", "normal", "high"],
        default="normal",
        help_text="Traffic condition level",
    )
    demand_level = serializers.ChoiceField(
        choices=["normal", "peak"], default="normal", help_text="Demand surge level"
    )

    def validate_traffic_level(self, value):
        valid_levels = ["low", "normal", "high"]
        if value not in valid_levels:
            raise serializers.ValidationError(
                f"Invalid traffic level. Allowed values: {', '.join(valid_levels)}"
            )
        return value

    def validate_demand_level(self, value):
        valid_levels = ["normal", "peak"]
        if value not in valid_levels:
            raise serializers.ValidationError(
                f"Invalid demand level. Allowed values: {', '.join(valid_levels)}"
            )
        return value


class FareCalculationResponseSerializer(serializers.Serializer):
    base_fare = serializers.FloatField()
    distance_fare = serializers.FloatField()
    multipliers = serializers.DictField()
    total_fare = serializers.FloatField()
