from rest_framework import serializers
from .models import Room, Booking, Landlord, Tenant, CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'role']

class LandlordSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Landlord
        fields = ['id', 'user', 'phone_number', 'dorm_name', 'address', 'bank_name', 'bank_account_number', 'account_holder_name']

class TenantSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Tenant
        fields = ['id', 'user', 'budget', 'preferences']

class RoomSerializer(serializers.ModelSerializer):
    landlord = LandlordSerializer(read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'landlord', 'dorm_name', 'room_name', 'image', 'price', 'location',
            'lease_duration_months', 'table_count', 'bed_count', 'chair_count', 'aircon_count',
            'sofa_count', 'wardrobe_count', 'desk_count', 'tv_count', 'refrigerator_count',
            'water_heater_count', 'size', 'description', 'available', 'created_at'
        ]

class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source='room', write_only=True
    )
    tenant_id = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(), source='tenant', write_only=True, required=False
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'room', 'room_id', 'tenant', 'tenant_id', 'full_name', 'phone', 'email',
            'check_in', 'check_out', 'status', 'created_at'
        ]

    def validate(self, data):
        # Ensure check_in is not in the past
        if data.get('check_in') and data['check_in'] < date.today():
            raise serializers.ValidationError({"check_in": "Check-in date cannot be in the past."})
        # Ensure either tenant or guest details are provided
        if not data.get('tenant') and not (data.get('full_name') and data.get('phone') and data.get('email')):
            raise serializers.ValidationError("Either a tenant or guest details (full_name, phone, and email) must be provided.")
        return data