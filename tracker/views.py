from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Q
from django.http import JsonResponse

from .models import (
    Household, EnergyUsage, Transportation, Diet,
    CarbonFootprint, ReductionTip, UserReductionGoal, EmissionFactor
)
from .serializers import (
    HouseholdSerializer, HouseholdCreateSerializer, EnergyUsageSerializer,
    TransportationSerializer, DietSerializer, CarbonFootprintSerializer,
    ReductionTipSerializer, UserReductionGoalSerializer, EmissionFactorSerializer,
    CarbonFootprintSummarySerializer
)
from .services import CarbonFootprintCalculator, ReductionTipService


class HouseholdViewSet(viewsets.ModelViewSet):
    """ViewSet for managing households"""
    serializer_class = HouseholdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(members=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return HouseholdCreateSerializer
        return HouseholdSerializer

    def perform_create(self, serializer):
        household = serializer.save()
        household.members.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the household"""
        household = self.get_object()
        username = request.data.get('username')
        
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=username)
            household.members.add(user)
            return Response({'message': f'User {username} added to household'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def footprint_summary(self, request, pk=None):
        """Get carbon footprint summary for household"""
        household = self.get_object()
        calculator = CarbonFootprintCalculator(household)
        
        # Get or calculate latest footprint
        latest_footprint = household.footprints.first()
        if not latest_footprint:
            latest_footprint = calculator.calculate_total_footprint()
        
        # Get comparison data
        comparison_data = calculator.get_comparison_data()
        
        # Get recommendations
        recommendations = calculator.get_reduction_recommendations(latest_footprint)
        
        # Get trend data (last 12 months)
        trend_data = []
        for i in range(12):
            date = datetime.now().date() - timedelta(days=30*i)
            footprint = household.footprints.filter(calculation_date__month=date.month, calculation_date__year=date.year).first()
            if footprint:
                trend_data.append({
                    'date': footprint.calculation_date.strftime('%Y-%m'),
                    'total_emissions': footprint.total_emissions,
                    'energy_emissions': footprint.energy_emissions,
                    'transportation_emissions': footprint.transportation_emissions,
                    'diet_emissions': footprint.diet_emissions,
                })
        
        summary_data = {
            'total_emissions': latest_footprint.total_emissions,
            'total_tons': round(latest_footprint.total_emissions / 1000, 2),
            'per_capita_emissions': latest_footprint.per_capita_emissions,
            'per_capita_tons': round(latest_footprint.per_capita_emissions / 1000, 2),
            'energy_emissions': latest_footprint.energy_emissions,
            'transportation_emissions': latest_footprint.transportation_emissions,
            'diet_emissions': latest_footprint.diet_emissions,
            'comparison_data': comparison_data,
            'recommendations': recommendations,
            'trend_data': trend_data,
        }
        
        serializer = CarbonFootprintSummarySerializer(summary_data)
        return Response(serializer.data)


class EnergyUsageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing energy usage data"""
    serializer_class = EnergyUsageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_households = Household.objects.filter(members=self.request.user)
        return EnergyUsage.objects.filter(household__in=user_households)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TransportationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing transportation data"""
    serializer_class = TransportationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_households = Household.objects.filter(members=self.request.user)
        return Transportation.objects.filter(household__in=user_households)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DietViewSet(viewsets.ModelViewSet):
    """ViewSet for managing diet data"""
    serializer_class = DietSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_households = Household.objects.filter(members=self.request.user)
        return Diet.objects.filter(household__in=user_households)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CarbonFootprintViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing carbon footprint data"""
    serializer_class = CarbonFootprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_households = Household.objects.filter(members=self.request.user)
        return CarbonFootprint.objects.filter(household__in=user_households)

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate carbon footprint for a household"""
        household_id = request.data.get('household_id')
        if not household_id:
            return Response({'error': 'household_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            household = Household.objects.get(id=household_id, members=request.user)
            calculator = CarbonFootprintCalculator(household)
            footprint = calculator.calculate_total_footprint()
            serializer = self.get_serializer(footprint)
            return Response(serializer.data)
        except Household.DoesNotExist:
            return Response({'error': 'Household not found'}, status=status.HTTP_404_NOT_FOUND)


class ReductionTipViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing reduction tips"""
    serializer_class = ReductionTipSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ReductionTip.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def personalized(self, request):
        """Get personalized tips for user's household"""
        household_id = request.query_params.get('household_id')
        if not household_id:
            return Response({'error': 'household_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            household = Household.objects.get(id=household_id, members=request.user)
            tips = ReductionTipService.get_personalized_tips(household)
            serializer = self.get_serializer(tips, many=True)
            return Response(serializer.data)
        except Household.DoesNotExist:
            return Response({'error': 'Household not found'}, status=status.HTTP_404_NOT_FOUND)


class UserReductionGoalViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user reduction goals"""
    serializer_class = UserReductionGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_households = Household.objects.filter(members=self.request.user)
        return UserReductionGoal.objects.filter(household__in=user_households)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmissionFactorViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing emission factors"""
    serializer_class = EmissionFactorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = EmissionFactor.objects.filter(is_active=True)


# Template-based views for the web interface

@login_required
def dashboard(request):
    """Main dashboard view"""
    user_households = Household.objects.filter(members=request.user)
    
    # Handle household creation via POST
    if request.method == 'POST' and request.POST.get('action') == 'create_household':
        try:
            household = Household.objects.create(
                name=request.POST.get('name'),
                household_size=int(request.POST.get('household_size', 1)),
                address=request.POST.get('address', ''),
                created_by=request.user
            )
            household.members.add(request.user)
            messages.success(request, f'Household "{household.name}" created successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error creating household: {str(e)}')
            return redirect('dashboard')
    
    context = {
        'households': user_households,
        'user': request.user,
    }
    
    # Get data for the first household if available
    if user_households.exists():
        household = user_households.first()
        calculator = CarbonFootprintCalculator(household)
        
        # Get or calculate latest footprint
        latest_footprint = household.footprints.first()
        if not latest_footprint:
            latest_footprint = calculator.calculate_total_footprint()
        
        # Get personalized tips
        tips = ReductionTipService.get_personalized_tips(household)
        
        context.update({
            'current_household': household,
            'footprint': latest_footprint,
            'tips': tips[:5],  # Show top 5 tips
        })
    
    return render(request, 'tracker/dashboard.html', context)


@login_required
def create_household(request):
    """Create household via AJAX"""
    if request.method == 'POST':
        try:
            household = Household.objects.create(
                name=request.POST.get('name'),
                household_size=int(request.POST.get('household_size', 1)),
                address=request.POST.get('address', ''),
                created_by=request.user
            )
            household.members.add(request.user)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Household "{household.name}" created successfully!',
                    'household_id': household.id
                })
            else:
                messages.success(request, f'Household "{household.name}" created successfully!')
                return redirect('dashboard')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating household: {str(e)}'
                })
            else:
                messages.error(request, f'Error creating household: {str(e)}')
                return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def household_detail(request, household_id):
    """Detailed view for a specific household"""
    household = get_object_or_404(Household, id=household_id, members=request.user)
    calculator = CarbonFootprintCalculator(household)
    
    # Get or calculate latest footprint
    latest_footprint = household.footprints.first()
    if not latest_footprint:
        latest_footprint = calculator.calculate_total_footprint()
    
    # Get recent data
    recent_energy = household.energy_usage.all()[:10]
    recent_transportation = household.transportation.all()[:10]
    recent_diet = household.diet.all()[:10]
    
    # Get personalized tips
    tips = ReductionTipService.get_personalized_tips(household)
    
    context = {
        'household': household,
        'footprint': latest_footprint,
        'recent_energy': recent_energy,
        'recent_transportation': recent_transportation,
        'recent_diet': recent_diet,
        'tips': tips,
    }
    
    return render(request, 'tracker/household_detail.html', context)


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            
            # Log the user in
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
                return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def add_data(request):
    """View for adding new data entries"""
    if request.method == 'POST':
        data_type = request.POST.get('data_type')
        household_id = request.POST.get('household')
        
        try:
            household = Household.objects.get(id=household_id, members=request.user)
            
            if data_type == 'energy':
                EnergyUsage.objects.create(
                    household=household,
                    energy_type=request.POST.get('energy_type'),
                    usage_amount=float(request.POST.get('usage_amount')),
                    unit=request.POST.get('unit', 'kWh'),
                    bill_amount=request.POST.get('bill_amount') or None,
                    date_recorded=request.POST.get('date_recorded'),
                    created_by=request.user
                )
                messages.success(request, 'Energy usage data added successfully!')
                
            elif data_type == 'transportation':
                Transportation.objects.create(
                    household=household,
                    transport_type=request.POST.get('transport_type'),
                    distance=float(request.POST.get('distance')),
                    frequency=request.POST.get('frequency', 'daily'),
                    fuel_efficiency=request.POST.get('fuel_efficiency') or None,
                    date_recorded=request.POST.get('date_recorded'),
                    created_by=request.user
                )
                messages.success(request, 'Transportation data added successfully!')
                
            elif data_type == 'diet':
                Diet.objects.create(
                    household=household,
                    diet_type=request.POST.get('diet_type'),
                    food_category=request.POST.get('food_category'),
                    weekly_consumption=float(request.POST.get('weekly_consumption')),
                    local_sourced_percentage=int(request.POST.get('local_sourced_percentage', 0)),
                    organic_percentage=int(request.POST.get('organic_percentage', 0)),
                    date_recorded=request.POST.get('date_recorded'),
                    created_by=request.user
                )
                messages.success(request, 'Diet data added successfully!')
                
        except (Household.DoesNotExist, ValueError) as e:
            messages.error(request, f'Error adding data: {str(e)}')
        
        return redirect('dashboard')
    
    user_households = Household.objects.filter(members=request.user)
    context = {
        'households': user_households,
        'energy_types': EnergyUsage.ENERGY_TYPES,
        'transport_types': Transportation.TRANSPORT_TYPES,
        'diet_types': Diet.DIET_TYPES,
        'food_categories': Diet.FOOD_CATEGORIES,
    }
    
    return render(request, 'tracker/add_data.html', context)
