"""
Carbon footprint calculation services
"""
from datetime import datetime, timedelta
from django.db.models import Sum, Q
from .models import (
    Household, EnergyUsage, Transportation, Diet, 
    CarbonFootprint, EmissionFactor
)


class CarbonFootprintCalculator:
    """Service class for calculating carbon footprints"""
    
    # Default emission factors (kg CO2 per unit)
    DEFAULT_EMISSION_FACTORS = {
        # Energy (kg CO2 per kWh/unit)
        'electricity': 0.4,  # kg CO2 per kWh (US average)
        'gas': 2.0,          # kg CO2 per therm
        'oil': 2.5,          # kg CO2 per gallon
        'propane': 5.7,      # kg CO2 per gallon
        'coal': 0.9,         # kg CO2 per kWh
        'solar': 0.04,       # kg CO2 per kWh
        'wind': 0.01,        # kg CO2 per kWh
        
        # Transportation (kg CO2 per mile)
        'car_gasoline': 0.4,      # kg CO2 per mile
        'car_diesel': 0.45,       # kg CO2 per mile
        'car_hybrid': 0.2,        # kg CO2 per mile
        'car_electric': 0.15,     # kg CO2 per mile (considering electricity source)
        'motorcycle': 0.3,        # kg CO2 per mile
        'bus': 0.1,              # kg CO2 per mile per passenger
        'train': 0.05,           # kg CO2 per mile per passenger
        'subway': 0.04,          # kg CO2 per mile per passenger
        'flight_domestic': 0.4,   # kg CO2 per mile
        'flight_international': 0.5,  # kg CO2 per mile
        'bike': 0.0,             # kg CO2 per mile
        'walk': 0.0,             # kg CO2 per mile
        
        # Diet (kg CO2 per serving per week)
        'meat_beef': 6.0,        # kg CO2 per serving per week
        'meat_pork': 2.4,        # kg CO2 per serving per week
        'meat_chicken': 1.2,     # kg CO2 per serving per week
        'meat_lamb': 5.2,        # kg CO2 per serving per week
        'fish': 1.5,             # kg CO2 per serving per week
        'dairy': 0.9,            # kg CO2 per serving per week
        'eggs': 0.4,             # kg CO2 per serving per week
        'vegetables': 0.1,       # kg CO2 per serving per week
        'fruits': 0.2,           # kg CO2 per serving per week
        'grains': 0.3,           # kg CO2 per serving per week
        'processed': 1.0,        # kg CO2 per serving per week
    }
    
    def __init__(self, household):
        self.household = household
        
    def get_emission_factor(self, category, name):
        """Get emission factor from database or use default"""
        try:
            factor = EmissionFactor.objects.get(
                category=category, 
                name=name, 
                is_active=True
            )
            return factor.factor_value
        except EmissionFactor.DoesNotExist:
            return self.DEFAULT_EMISSION_FACTORS.get(name, 0.0)
    
    def calculate_energy_emissions(self, start_date=None, end_date=None):
        """Calculate energy-related carbon emissions"""
        energy_usage = self.household.energy_usage.all()
        
        if start_date and end_date:
            energy_usage = energy_usage.filter(
                date_recorded__range=[start_date, end_date]
            )
        
        total_emissions = 0.0
        
        for usage in energy_usage:
            emission_factor = self.get_emission_factor('energy', usage.energy_type)
            emissions = usage.usage_amount * emission_factor
            total_emissions += emissions
            
        return total_emissions
    
    def calculate_transportation_emissions(self, start_date=None, end_date=None):
        """Calculate transportation-related carbon emissions"""
        transportation = self.household.transportation.all()
        
        if start_date and end_date:
            transportation = transportation.filter(
                date_recorded__range=[start_date, end_date]
            )
        
        total_emissions = 0.0
        
        for transport in transportation:
            emission_factor = self.get_emission_factor('transportation', transport.transport_type)
            
            # Calculate annual distance based on frequency
            frequency_multipliers = {
                'daily': 365,
                'weekly': 52,
                'monthly': 12,
                'yearly': 1
            }
            
            multiplier = frequency_multipliers.get(transport.frequency, 1)
            annual_distance = transport.distance * multiplier
            
            emissions = annual_distance * emission_factor
            total_emissions += emissions
            
        return total_emissions
    
    def calculate_diet_emissions(self, start_date=None, end_date=None):
        """Calculate diet-related carbon emissions"""
        diet_data = self.household.diet.all()
        
        if start_date and end_date:
            diet_data = diet_data.filter(
                date_recorded__range=[start_date, end_date]
            )
        
        total_emissions = 0.0
        
        for diet_item in diet_data:
            base_emission_factor = self.get_emission_factor('diet', diet_item.food_category)
            
            # Adjust for local sourcing (reduces emissions by up to 20%)
            local_reduction = (diet_item.local_sourced_percentage / 100) * 0.2
            
            # Adjust for organic (may increase emissions slightly due to lower yields)
            organic_adjustment = (diet_item.organic_percentage / 100) * 0.1
            
            adjusted_factor = base_emission_factor * (1 - local_reduction + organic_adjustment)
            
            # Calculate annual emissions (weekly consumption * 52 weeks)
            annual_emissions = diet_item.weekly_consumption * adjusted_factor * 52
            total_emissions += annual_emissions
            
        return total_emissions
    
    def calculate_total_footprint(self, calculation_date=None):
        """Calculate total carbon footprint for the household"""
        if not calculation_date:
            calculation_date = datetime.now().date()
        
        # Calculate emissions for the past year
        start_date = calculation_date - timedelta(days=365)
        end_date = calculation_date
        
        energy_emissions = self.calculate_energy_emissions(start_date, end_date)
        transportation_emissions = self.calculate_transportation_emissions(start_date, end_date)
        diet_emissions = self.calculate_diet_emissions(start_date, end_date)
        
        # Create or update carbon footprint record
        footprint, created = CarbonFootprint.objects.get_or_create(
            household=self.household,
            calculation_date=calculation_date,
            defaults={
                'energy_emissions': energy_emissions,
                'transportation_emissions': transportation_emissions,
                'diet_emissions': diet_emissions,
            }
        )
        
        if not created:
            footprint.energy_emissions = energy_emissions
            footprint.transportation_emissions = transportation_emissions
            footprint.diet_emissions = diet_emissions
            footprint.save()
        
        return footprint
    
    def get_comparison_data(self):
        """Get comparison data with national and global averages"""
        # US national average: ~16 tons CO2 per person per year
        # Global average: ~4.8 tons CO2 per person per year
        return {
            'national_average': 16000,  # kg CO2 per person per year
            'global_average': 4800,     # kg CO2 per person per year
        }
    
    def get_reduction_recommendations(self, footprint):
        """Get personalized reduction recommendations based on footprint"""
        recommendations = []
        
        # Energy recommendations
        if footprint.energy_emissions > 5000:  # Above average
            recommendations.extend([
                'Switch to LED light bulbs',
                'Improve home insulation',
                'Use a programmable thermostat',
                'Consider renewable energy sources'
            ])
        
        # Transportation recommendations
        if footprint.transportation_emissions > 3000:  # Above average
            recommendations.extend([
                'Use public transportation more often',
                'Consider carpooling or ride-sharing',
                'Walk or bike for short trips',
                'Work from home when possible'
            ])
        
        # Diet recommendations
        if footprint.diet_emissions > 2000:  # Above average
            recommendations.extend([
                'Reduce meat consumption, especially beef',
                'Buy local and seasonal produce',
                'Reduce food waste',
                'Consider plant-based alternatives'
            ])
        
        return recommendations


class ReductionTipService:
    """Service for managing reduction tips and recommendations"""
    
    @staticmethod
    def get_personalized_tips(household):
        """Get personalized tips based on household's carbon footprint"""
        calculator = CarbonFootprintCalculator(household)
        latest_footprint = household.footprints.first()
        
        if not latest_footprint:
            latest_footprint = calculator.calculate_total_footprint()
        
        tips = []
        
        # Get tips based on highest emission categories
        emissions_by_category = [
            ('energy', latest_footprint.energy_emissions),
            ('transportation', latest_footprint.transportation_emissions),
            ('diet', latest_footprint.diet_emissions),
        ]
        
        # Sort by emissions (highest first)
        emissions_by_category.sort(key=lambda x: x[1], reverse=True)
        
        # Get tips for the top 2 categories
        from .models import ReductionTip
        for category, _ in emissions_by_category[:2]:
            category_tips = ReductionTip.objects.filter(
                category=category,
                is_active=True
            ).order_by('-potential_savings')[:3]
            tips.extend(category_tips)
        
        return tips
    
    @staticmethod
    def calculate_potential_impact(household, tip):
        """Calculate potential impact of implementing a reduction tip"""
        calculator = CarbonFootprintCalculator(household)
        current_footprint = calculator.calculate_total_footprint()
        
        # Estimate impact based on tip category and current emissions
        category_emissions = {
            'energy': current_footprint.energy_emissions,
            'transportation': current_footprint.transportation_emissions,
            'diet': current_footprint.diet_emissions,
        }
        
        current_category_emissions = category_emissions.get(tip.category, 0)
        potential_reduction = min(tip.potential_savings, current_category_emissions * 0.3)
        
        return {
            'potential_reduction': potential_reduction,
            'percentage_reduction': (potential_reduction / current_footprint.total_emissions) * 100 if current_footprint.total_emissions > 0 else 0,
            'new_total_emissions': current_footprint.total_emissions - potential_reduction
        }