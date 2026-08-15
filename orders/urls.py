from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderStatsView

router = DefaultRouter()
router.include_format_suffixes = False
router.register('', OrderViewSet, basename='order')

urlpatterns = [
    path('stats/', OrderStatsView.as_view(), name='order-stats'),
] + router.urls
