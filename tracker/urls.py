from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API router
router = DefaultRouter()
router.register(r'households', views.HouseholdViewSet, basename='household')
router.register(r'energy-usage', views.EnergyUsageViewSet, basename='energyusage')
router.register(r'transportation', views.TransportationViewSet, basename='transportation')
router.register(r'diet', views.DietViewSet, basename='diet')
router.register(r'carbon-footprints', views.CarbonFootprintViewSet, basename='carbonfootprint')
router.register(r'reduction-tips', views.ReductionTipViewSet, basename='reductiontip')
router.register(r'reduction-goals', views.UserReductionGoalViewSet, basename='reductiongoal')
router.register(r'emission-factors', views.EmissionFactorViewSet, basename='emissionfactor')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Web interface URLs
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('add-data/', views.add_data, name='add_data'),
    path('household/<int:household_id>/', views.household_detail, name='household_detail'),
]