"""
URL configuration for SMS Webhook application
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST API router
router = DefaultRouter()
router.register(r'sms', views.SMSMessageViewSet, basename='sms')
router.register(r'mpesa', views.MPESATransactionViewSet, basename='mpesa')

# Web interface URLs
urlpatterns = [
    # Webhook endpoint for SMSMobileAPI
    path('webhook/sms/', views.WebhookView.as_view(), name='webhook_sms'),
    
    # Web interface
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('sms/', views.SMSListView.as_view(), name='sms_list'),
    path('mpesa/', views.MPESAListView.as_view(), name='mpesa_list'),
    
    # REST API
    path('api/', include(router.urls)),
]

# Add API endpoints for statistics
urlpatterns += [
    path('api/mpesa/statistics/', views.MPESATransactionViewSet.as_view({'get': 'statistics'}), name='mpesa_statistics'),
]
