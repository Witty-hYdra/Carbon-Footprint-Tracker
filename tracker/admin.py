from django.contrib import admin
from .models import (
    Household, EnergyUsage, Transportation, Diet, 
    CarbonFootprint, ReductionTip, UserReductionGoal, EmissionFactor
)


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'household_size', 'created_at']
    list_filter = ['created_at', 'household_size']
    search_fields = ['name', 'created_by__username']
    filter_horizontal = ['members']


@admin.register(EnergyUsage)
class EnergyUsageAdmin(admin.ModelAdmin):
    list_display = ['household', 'energy_type', 'usage_amount', 'unit', 'date_recorded']
    list_filter = ['energy_type', 'date_recorded', 'created_at']
    search_fields = ['household__name']
    date_hierarchy = 'date_recorded'


@admin.register(Transportation)
class TransportationAdmin(admin.ModelAdmin):
    list_display = ['household', 'transport_type', 'distance', 'frequency', 'date_recorded']
    list_filter = ['transport_type', 'frequency', 'date_recorded']
    search_fields = ['household__name']
    date_hierarchy = 'date_recorded'


@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    list_display = ['household', 'diet_type', 'food_category', 'weekly_consumption', 'date_recorded']
    list_filter = ['diet_type', 'food_category', 'date_recorded']
    search_fields = ['household__name']
    date_hierarchy = 'date_recorded'


@admin.register(CarbonFootprint)
class CarbonFootprintAdmin(admin.ModelAdmin):
    list_display = [
        'household', 'calculation_date', 'total_emissions', 
        'per_capita_emissions', 'energy_emissions', 'transportation_emissions', 'diet_emissions'
    ]
    list_filter = ['calculation_date']
    search_fields = ['household__name']
    date_hierarchy = 'calculation_date'
    readonly_fields = ['total_emissions', 'per_capita_emissions']


@admin.register(ReductionTip)
class ReductionTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'potential_savings', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active']


@admin.register(UserReductionGoal)
class UserReductionGoalAdmin(admin.ModelAdmin):
    list_display = [
        'household', 'reduction_tip', 'target_date', 
        'is_completed', 'completion_date', 'created_by'
    ]
    list_filter = ['is_completed', 'target_date', 'completion_date']
    search_fields = ['household__name', 'reduction_tip__title']
    date_hierarchy = 'target_date'


@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'factor_value', 'unit', 'is_active', 'last_updated']
    list_filter = ['category', 'is_active', 'last_updated']
    search_fields = ['name', 'category']
    list_editable = ['is_active']
