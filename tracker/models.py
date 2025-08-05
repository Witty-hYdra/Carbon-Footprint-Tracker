from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Household(models.Model):
    """Model to represent a household with multiple users"""
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_households')
    members = models.ManyToManyField(User, related_name='households')
    address = models.TextField(blank=True, null=True)
    household_size = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class EnergyUsage(models.Model):
    """Model to track household energy usage"""
    ENERGY_TYPES = [
        ('electricity', 'Electricity'),
        ('gas', 'Natural Gas'),
        ('oil', 'Heating Oil'),
        ('propane', 'Propane'),
        ('coal', 'Coal'),
        ('solar', 'Solar'),
        ('wind', 'Wind'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='energy_usage')
    energy_type = models.CharField(max_length=20, choices=ENERGY_TYPES)
    usage_amount = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='kWh')  # kWh, therms, gallons, etc.
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_recorded = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.energy_type} - {self.usage_amount} {self.unit}"

    class Meta:
        ordering = ['-date_recorded']


class Transportation(models.Model):
    """Model to track transportation activities"""
    TRANSPORT_TYPES = [
        ('car_gasoline', 'Car (Gasoline)'),
        ('car_diesel', 'Car (Diesel)'),
        ('car_hybrid', 'Car (Hybrid)'),
        ('car_electric', 'Car (Electric)'),
        ('motorcycle', 'Motorcycle'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('subway', 'Subway'),
        ('flight_domestic', 'Flight (Domestic)'),
        ('flight_international', 'Flight (International)'),
        ('bike', 'Bicycle'),
        ('walk', 'Walking'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='transportation')
    transport_type = models.CharField(max_length=30, choices=TRANSPORT_TYPES)
    distance = models.FloatField(validators=[MinValueValidator(0)])  # in miles or km
    frequency = models.CharField(max_length=20, default='daily')  # daily, weekly, monthly
    fuel_efficiency = models.FloatField(null=True, blank=True)  # mpg or km/l
    date_recorded = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.transport_type} - {self.distance} miles"

    class Meta:
        ordering = ['-date_recorded']


class Diet(models.Model):
    """Model to track dietary habits and food consumption"""
    DIET_TYPES = [
        ('omnivore', 'Omnivore'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('flexitarian', 'Flexitarian'),
    ]

    FOOD_CATEGORIES = [
        ('meat_beef', 'Beef'),
        ('meat_pork', 'Pork'),
        ('meat_chicken', 'Chicken'),
        ('meat_lamb', 'Lamb'),
        ('fish', 'Fish'),
        ('dairy', 'Dairy Products'),
        ('eggs', 'Eggs'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains'),
        ('processed', 'Processed Foods'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='diet')
    diet_type = models.CharField(max_length=20, choices=DIET_TYPES)
    food_category = models.CharField(max_length=20, choices=FOOD_CATEGORIES)
    weekly_consumption = models.FloatField(validators=[MinValueValidator(0)])  # servings per week
    local_sourced_percentage = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    organic_percentage = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    date_recorded = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.food_category} - {self.weekly_consumption} servings/week"

    class Meta:
        ordering = ['-date_recorded']


class CarbonFootprint(models.Model):
    """Model to store calculated carbon footprint data"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='footprints')
    calculation_date = models.DateField()
    
    # Carbon emissions by category (in kg CO2 equivalent)
    energy_emissions = models.FloatField(default=0.0)
    transportation_emissions = models.FloatField(default=0.0)
    diet_emissions = models.FloatField(default=0.0)
    total_emissions = models.FloatField(default=0.0)
    
    # Per capita emissions
    per_capita_emissions = models.FloatField(default=0.0)
    
    # Comparison data
    national_average = models.FloatField(null=True, blank=True)
    global_average = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate total emissions
        self.total_emissions = (
            self.energy_emissions + 
            self.transportation_emissions + 
            self.diet_emissions
        )
        
        # Calculate per capita emissions
        if self.household.household_size > 0:
            self.per_capita_emissions = self.total_emissions / self.household.household_size
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.household.name} - {self.calculation_date} - {self.total_emissions:.2f} kg CO2"

    class Meta:
        ordering = ['-calculation_date']
        unique_together = ['household', 'calculation_date']


class ReductionTip(models.Model):
    """Model to store carbon footprint reduction tips and recommendations"""
    CATEGORIES = [
        ('energy', 'Energy'),
        ('transportation', 'Transportation'),
        ('diet', 'Diet'),
        ('waste', 'Waste'),
        ('water', 'Water'),
        ('general', 'General'),
    ]

    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS)
    potential_savings = models.FloatField(help_text="Potential CO2 savings in kg per year")
    cost_estimate = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['category', '-potential_savings']


class UserReductionGoal(models.Model):
    """Model to track user reduction goals and progress"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='goals')
    reduction_tip = models.ForeignKey(ReductionTip, on_delete=models.CASCADE)
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.household.name} - {self.reduction_tip.title}"

    class Meta:
        ordering = ['-created_at']


class EmissionFactor(models.Model):
    """Model to store emission factors for calculations"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    factor_value = models.FloatField()  # kg CO2 per unit
    unit = models.CharField(max_length=20)
    source = models.CharField(max_length=200, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.factor_value} kg CO2/{self.unit}"

    class Meta:
        ordering = ['category', 'name']
