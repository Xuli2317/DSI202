from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Room, Booking, Landlord, Tenant
from .serializers import RoomSerializer, BookingSerializer, LandlordSerializer, TenantSerializer
from django.shortcuts import get_object_or_404

class IsLandlord(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'landlord'

class IsTenant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tenant'

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsLandlord()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user.landlord_profile)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsTenant()]
        elif self.action == 'cancel':
            return [IsTenant()]
        return [permissions.AllowAny()]

    @action(detail=True, methods=['post'], permission_classes=[IsTenant])
    def cancel(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk, tenant__user=request.user)
        booking.status = 'canceled'
        booking.save()
        return Response({'status': 'Booking canceled'})

class LandlordViewSet(viewsets.ModelViewSet):
    queryset = Landlord.objects.all()
    serializer_class = LandlordSerializer
    permission_classes = [IsLandlord]

    def get_queryset(self):
        return Landlord.objects.filter(user=self.request.user)

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsTenant]

    def get_queryset(self):
        return Tenant.objects.filter(user=self.request.user)