from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import RoomViewSet, BookingViewSet, LandlordViewSet, TenantViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'landlords', LandlordViewSet)
router.register(r'tenants', TenantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]