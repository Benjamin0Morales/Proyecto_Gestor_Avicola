"""
URL configuration for the API app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api import views

# Create router and register viewsets
router = DefaultRouter()

# Production endpoints
router.register(r'farm-status', views.FarmStatusViewSet, basename='farm-status')
router.register(r'egg-production', views.EggProductionViewSet, basename='egg-production')
router.register(r'mortality-events', views.MortalityEventViewSet, basename='mortality-events')
router.register(r'feed-items', views.FeedItemViewSet, basename='feed-items')
router.register(r'feed-mixes', views.FeedMixViewSet, basename='feed-mixes')
router.register(r'feed-mix-items', views.FeedMixItemViewSet, basename='feed-mix-items')
router.register(r'feed-consumption', views.FeedConsumptionViewSet, basename='feed-consumption')

# Finance endpoints
router.register(r'finance/categories', views.FinanceCategoryViewSet, basename='finance-categories')
router.register(r'finance/transactions', views.FinanceTransactionViewSet, basename='finance-transactions')
router.register(r'finance/summary', views.FinanceSummaryViewSet, basename='finance-summary')

# Report endpoints
router.register(r'reports', views.ReportExportViewSet, basename='reports')

urlpatterns = [
    # Authentication
    path('auth/login/', views.login_view, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Router URLs
    path('', include(router.urls)),
]
