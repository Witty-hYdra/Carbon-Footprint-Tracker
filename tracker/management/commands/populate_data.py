from django.core.management.base import BaseCommand
from tracker.models import ReductionTip, EmissionFactor


class Command(BaseCommand):
    help = 'Populate database with initial reduction tips and emission factors'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with initial data...')
        
        # Create reduction tips
        tips_data = [
            {
                'title': 'Switch to LED Light Bulbs',
                'description': 'Replace incandescent and CFL bulbs with energy-efficient LED bulbs. LEDs use up to 75% less energy and last 25 times longer.',
                'category': 'energy',
                'difficulty': 'easy',
                'potential_savings': 200,
                'cost_estimate': '$20-50'
            },
            {
                'title': 'Improve Home Insulation',
                'description': 'Add insulation to your attic, walls, and basement to reduce heating and cooling costs. Proper insulation can save up to 15% on heating and cooling costs.',
                'category': 'energy',
                'difficulty': 'medium',
                'potential_savings': 800,
                'cost_estimate': '$500-2000'
            },
            {
                'title': 'Install a Programmable Thermostat',
                'description': 'A programmable thermostat can automatically adjust temperature when you\'re away or sleeping, saving energy without sacrificing comfort.',
                'category': 'energy',
                'difficulty': 'medium',
                'potential_savings': 300,
                'cost_estimate': '$100-250'
            },
            {
                'title': 'Use Public Transportation',
                'description': 'Take buses, trains, or subways instead of driving alone. Public transportation produces significantly lower emissions per passenger mile.',
                'category': 'transportation',
                'difficulty': 'easy',
                'potential_savings': 1200,
                'cost_estimate': 'Varies by location'
            },
            {
                'title': 'Work from Home When Possible',
                'description': 'Remote work eliminates commuting emissions entirely. Even working from home 2 days a week can significantly reduce your transportation footprint.',
                'category': 'transportation',
                'difficulty': 'easy',
                'potential_savings': 800,
                'cost_estimate': 'Free'
            },
            {
                'title': 'Consider an Electric Vehicle',
                'description': 'Electric vehicles produce zero direct emissions and are becoming more affordable. Even accounting for electricity generation, EVs typically have lower lifetime emissions.',
                'category': 'transportation',
                'difficulty': 'hard',
                'potential_savings': 2000,
                'cost_estimate': '$25,000-50,000'
            },
            {
                'title': 'Reduce Meat Consumption',
                'description': 'Livestock farming is a major source of greenhouse gases. Reducing meat consumption, especially beef, can significantly lower your diet-related emissions.',
                'category': 'diet',
                'difficulty': 'medium',
                'potential_savings': 600,
                'cost_estimate': 'May save money'
            },
            {
                'title': 'Buy Local and Seasonal Produce',
                'description': 'Locally grown, seasonal produce requires less transportation and storage, reducing associated emissions. Shop at farmers markets when possible.',
                'category': 'diet',
                'difficulty': 'easy',
                'potential_savings': 150,
                'cost_estimate': 'Similar to regular groceries'
            },
            {
                'title': 'Reduce Food Waste',
                'description': 'Plan meals, store food properly, and compost scraps. Food waste in landfills produces methane, a potent greenhouse gas.',
                'category': 'diet',
                'difficulty': 'easy',
                'potential_savings': 300,
                'cost_estimate': 'Saves money'
            },
            {
                'title': 'Install Solar Panels',
                'description': 'Generate clean, renewable energy for your home. Solar panels can significantly reduce or eliminate your electricity-related emissions.',
                'category': 'energy',
                'difficulty': 'hard',
                'potential_savings': 3000,
                'cost_estimate': '$15,000-25,000'
            },
            {
                'title': 'Reduce Water Heating Temperature',
                'description': 'Lower your water heater temperature to 120°F (49°C). This simple change can reduce water heating costs by 6-10%.',
                'category': 'energy',
                'difficulty': 'easy',
                'potential_savings': 150,
                'cost_estimate': 'Free'
            },
            {
                'title': 'Carpool or Use Ride-Sharing',
                'description': 'Share rides with others to reduce the number of vehicles on the road. Carpooling can cut your transportation emissions in half.',
                'category': 'transportation',
                'difficulty': 'easy',
                'potential_savings': 400,
                'cost_estimate': 'May save money'
            },
        ]

        for tip_data in tips_data:
            tip, created = ReductionTip.objects.get_or_create(
                title=tip_data['title'],
                defaults=tip_data
            )
            if created:
                self.stdout.write(f'Created tip: {tip.title}')

        # Create emission factors
        factors_data = [
            # Energy factors
            {'name': 'electricity', 'category': 'energy', 'factor_value': 0.4, 'unit': 'kWh'},
            {'name': 'gas', 'category': 'energy', 'factor_value': 2.0, 'unit': 'therm'},
            {'name': 'oil', 'category': 'energy', 'factor_value': 2.5, 'unit': 'gallon'},
            {'name': 'propane', 'category': 'energy', 'factor_value': 5.7, 'unit': 'gallon'},
            {'name': 'coal', 'category': 'energy', 'factor_value': 0.9, 'unit': 'kWh'},
            {'name': 'solar', 'category': 'energy', 'factor_value': 0.04, 'unit': 'kWh'},
            {'name': 'wind', 'category': 'energy', 'factor_value': 0.01, 'unit': 'kWh'},
            
            # Transportation factors
            {'name': 'car_gasoline', 'category': 'transportation', 'factor_value': 0.4, 'unit': 'mile'},
            {'name': 'car_diesel', 'category': 'transportation', 'factor_value': 0.45, 'unit': 'mile'},
            {'name': 'car_hybrid', 'category': 'transportation', 'factor_value': 0.2, 'unit': 'mile'},
            {'name': 'car_electric', 'category': 'transportation', 'factor_value': 0.15, 'unit': 'mile'},
            {'name': 'motorcycle', 'category': 'transportation', 'factor_value': 0.3, 'unit': 'mile'},
            {'name': 'bus', 'category': 'transportation', 'factor_value': 0.1, 'unit': 'mile'},
            {'name': 'train', 'category': 'transportation', 'factor_value': 0.05, 'unit': 'mile'},
            {'name': 'subway', 'category': 'transportation', 'factor_value': 0.04, 'unit': 'mile'},
            {'name': 'flight_domestic', 'category': 'transportation', 'factor_value': 0.4, 'unit': 'mile'},
            {'name': 'flight_international', 'category': 'transportation', 'factor_value': 0.5, 'unit': 'mile'},
            
            # Diet factors
            {'name': 'meat_beef', 'category': 'diet', 'factor_value': 6.0, 'unit': 'serving/week'},
            {'name': 'meat_pork', 'category': 'diet', 'factor_value': 2.4, 'unit': 'serving/week'},
            {'name': 'meat_chicken', 'category': 'diet', 'factor_value': 1.2, 'unit': 'serving/week'},
            {'name': 'meat_lamb', 'category': 'diet', 'factor_value': 5.2, 'unit': 'serving/week'},
            {'name': 'fish', 'category': 'diet', 'factor_value': 1.5, 'unit': 'serving/week'},
            {'name': 'dairy', 'category': 'diet', 'factor_value': 0.9, 'unit': 'serving/week'},
            {'name': 'eggs', 'category': 'diet', 'factor_value': 0.4, 'unit': 'serving/week'},
            {'name': 'vegetables', 'category': 'diet', 'factor_value': 0.1, 'unit': 'serving/week'},
            {'name': 'fruits', 'category': 'diet', 'factor_value': 0.2, 'unit': 'serving/week'},
            {'name': 'grains', 'category': 'diet', 'factor_value': 0.3, 'unit': 'serving/week'},
            {'name': 'processed', 'category': 'diet', 'factor_value': 1.0, 'unit': 'serving/week'},
        ]

        for factor_data in factors_data:
            factor, created = EmissionFactor.objects.get_or_create(
                name=factor_data['name'],
                category=factor_data['category'],
                defaults=factor_data
            )
            if created:
                self.stdout.write(f'Created emission factor: {factor.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with initial data!')
        )