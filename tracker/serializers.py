from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Household, EnergyUsage, Transportation, Diet,
    CarbonFootprint, ReductionTip, UserReductionGoal, EmissionFactor
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class HouseholdSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = [
            'id', 'name', 'created_by', 'members', 'member_count',
            'address', 'household_size', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.members.count()


class EnergyUsageSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    household_name = serializers.CharField(source='household.name', read_only=True)

    class Meta:
        model = EnergyUsage
        fields = [
            'id', 'household', 'household_name', 'energy_type', 'usage_amount',
            'unit', 'bill_amount', 'date_recorded', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']


class TransportationSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    household_name = serializers.CharField(source='household.name', read_only=True)

    class Meta:
        model = Transportation
        fields = [
            'id', 'household', 'household_name', 'transport_type', 'distance',
            'frequency', 'fuel_efficiency', 'date_recorded', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']


class DietSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    household_name = serializers.CharField(source='household.name', read_only=True)

    class Meta:
        model = Diet
        fields = [
            'id', 'household', 'household_name', 'diet_type', 'food_category',
            'weekly_consumption', 'local_sourced_percentage', 'organic_percentage',
            'date_recorded', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']


class CarbonFootprintSerializer(serializers.ModelSerializer):
    household_name = serializers.CharField(source='household.name', read_only=True)
    per_capita_tons = serializers.SerializerMethodField()
    total_tons = serializers.SerializerMethodField()

    class Meta:
        model = CarbonFootprint
        fields = [
            'id', 'household', 'household_name', 'calculation_date',
            'energy_emissions', 'transportation_emissions', 'diet_emissions',
            'total_emissions', 'total_tons', 'per_capita_emissions', 'per_capita_tons',
            'national_average', 'global_average', 'created_at', 'updated_at'
        ]

    def get_per_capita_tons(self, obj):
        return round(obj.per_capita_emissions / 1000, 2)  # Convert kg to tons

    def get_total_tons(self, obj):
        return round(obj.total_emissions / 1000, 2)  # Convert kg to tons


class ReductionTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReductionTip
        fields = [
            'id', 'title', 'description', 'category', 'difficulty',
            'potential_savings', 'cost_estimate', 'is_active', 'created_at'
        ]


class UserReductionGoalSerializer(serializers.ModelSerializer):
    reduction_tip = ReductionTipSerializer(read_only=True)
    reduction_tip_id = serializers.IntegerField(write_only=True)
    household_name = serializers.CharField(source='household.name', read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = UserReductionGoal
        fields = [
            'id', 'household', 'household_name', 'reduction_tip', 'reduction_tip_id',
            'target_date', 'is_completed', 'completion_date', 'notes',
            'created_by', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']


class EmissionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactor
        fields = [
            'id', 'name', 'category', 'factor_value', 'unit',
            'source', 'last_updated', 'is_active'
        ]


class CarbonFootprintSummarySerializer(serializers.Serializer):
    """Serializer for carbon footprint summary data"""
    total_emissions = serializers.FloatField()
    total_tons = serializers.FloatField()
    per_capita_emissions = serializers.FloatField()
    per_capita_tons = serializers.FloatField()
    energy_emissions = serializers.FloatField()
    transportation_emissions = serializers.FloatField()
    diet_emissions = serializers.FloatField()
    comparison_data = serializers.DictField()
    recommendations = serializers.ListField(child=serializers.CharField())
    trend_data = serializers.ListField(child=serializers.DictField())


class HouseholdCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating households"""
    class Meta:
        model = Household
        fields = ['name', 'address', 'household_size']

    def create(self, validated_data):
        user = self.context['request'].user
        household = Household.objects.create(
            created_by=user,
            **validated_data
        )
        household.members.add(user)
        return household