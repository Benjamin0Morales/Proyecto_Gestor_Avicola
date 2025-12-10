"""
URL configuration for core web views.
Vistas organizadas por módulos para mejor mantenibilidad.
"""
from django.urls import path
from core import production_views, feed_views, finance_views, report_views, user_views, vision_views

urlpatterns = [
    # Users (Admin only)
    path('users/', user_views.user_list, name='user_list'),
    path('users/create/', user_views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', user_views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', user_views.user_delete, name='user_delete'),
    path('users/<int:pk>/activate/', user_views.user_activate, name='user_activate'),
    
    # ========================================================================
    # MÓDULO DE PRODUCCIÓN
    # ========================================================================
    
    # Farm Status
    path('farm-status/', production_views.farm_status_list, name='farm_status_list'),
    path('farm-status/create/', production_views.farm_status_create, name='farm_status_create'),
    path('farm-status/<int:pk>/edit/', production_views.farm_status_edit, name='farm_status_edit'),
    path('farm-status/<int:pk>/delete/', production_views.farm_status_delete, name='farm_status_delete'),
    
    # Egg Production
    path('egg-production/', production_views.egg_production_list, name='egg_production_list'),
    path('egg-production/create/', production_views.egg_production_create, name='egg_production_create'),
    path('egg-production/<int:pk>/edit/', production_views.egg_production_edit, name='egg_production_edit'),
    path('egg-production/<int:pk>/delete/', production_views.egg_production_delete, name='egg_production_delete'),
    
    # Vision Module (Computer Vision for Egg Counting)
    path('vision/count/', vision_views.vision_count_eggs, name='vision_count_eggs'),
    path('vision/confirm/', vision_views.vision_confirm, name='vision_confirm'),
    path('vision/cancel/', vision_views.vision_cancel, name='vision_cancel'),
    
    # Mortality Events
    path('mortality/', production_views.mortality_list, name='mortality_list'),
    path('mortality/create/', production_views.mortality_create, name='mortality_create'),
    path('mortality/<int:pk>/edit/', production_views.mortality_edit, name='mortality_edit'),
    path('mortality/<int:pk>/delete/', production_views.mortality_delete, name='mortality_delete'),
    
    # ========================================================================
    # MÓDULO DE ALIMENTACIÓN
    # ========================================================================
    
    # Feed Items
    path('feed-items/', feed_views.feed_item_list, name='feed_item_list'),
    path('feed-items/create/', feed_views.feed_item_create, name='feed_item_create'),
    path('feed-items/<int:pk>/edit/', feed_views.feed_item_edit, name='feed_item_edit'),
    path('feed-items/<int:pk>/delete/', feed_views.feed_item_delete, name='feed_item_delete'),
    
    # Feed Mixes
    path('feed-mixes/', feed_views.feed_mix_list, name='feed_mix_list'),
    path('feed-mixes/create/', feed_views.feed_mix_create, name='feed_mix_create'),
    path('feed-mixes/<int:pk>/edit/', feed_views.feed_mix_edit, name='feed_mix_edit'),
    path('feed-mixes/<int:pk>/delete/', feed_views.feed_mix_delete, name='feed_mix_delete'),
    
    # Feed Consumption
    path('feed-consumption/', feed_views.feed_consumption_list, name='feed_consumption_list'),
    path('feed-consumption/create/', feed_views.feed_consumption_create, name='feed_consumption_create'),
    path('feed-consumption/<int:pk>/edit/', feed_views.feed_consumption_edit, name='feed_consumption_edit'),
    path('feed-consumption/<int:pk>/delete/', feed_views.feed_consumption_delete, name='feed_consumption_delete'),
    
    # Feed Inventory
    path('feed-inventory/', feed_views.feed_inventory_list, name='feed_inventory_list'),
    path('feed-inventory/movements/', feed_views.feed_inventory_movements, name='feed_inventory_movements'),
    path('feed-inventory/movement/create/', feed_views.feed_inventory_movement_create, name='feed_inventory_movement_create'),
    
    # ========================================================================
    # MÓDULO DE FINANZAS
    # ========================================================================
    
    # Finance Categories
    path('finance/categories/', finance_views.finance_category_list, name='finance_category_list'),
    path('finance/categories/create/', finance_views.finance_category_create, name='finance_category_create'),
    path('finance/categories/<int:pk>/edit/', finance_views.finance_category_edit, name='finance_category_edit'),
    path('finance/categories/<int:pk>/delete/', finance_views.finance_category_delete, name='finance_category_delete'),
    
    # Finance Transactions
    path('finance/transactions/', finance_views.finance_transaction_list, name='finance_transaction_list'),
    path('finance/transactions/create/', finance_views.finance_transaction_create, name='finance_transaction_create'),
    path('finance/transactions/<int:pk>/edit/', finance_views.finance_transaction_edit, name='finance_transaction_edit'),
    path('finance/transactions/<int:pk>/delete/', finance_views.finance_transaction_delete, name='finance_transaction_delete'),
    
    # ========================================================================
    # MÓDULO DE REPORTES
    # ========================================================================
    
    # Financial Reports
    path('finance/summary/', report_views.financial_summary_view, name='financial_summary'),
    path('finance/export/pdf/', report_views.export_financial_pdf, name='export_financial_pdf'),
    path('finance/export/excel/', report_views.export_financial_excel, name='export_financial_excel'),
]
