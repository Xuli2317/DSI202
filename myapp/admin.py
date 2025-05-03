from django.contrib import admin
from .models import CustomUser, Tenant, Landlord, Room, Booking

# Custom CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'role')  
    search_fields = ('username', 'email', 'phone')  
    list_filter = ('role', 'is_active')

# Tenant Admin
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'budget')  
    search_fields = ('user__username', 'user__email')  

# Landlord Admin
@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')  
    search_fields = ('user__username', 'user__email')  

# Room Admin
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'dorm_name','room_name', 'price', 'location', 'available')
    search_fields = ('dorm_name', 'room_name', 'location', 'landlord__user__username')
    list_filter = ('available', 'price')

# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'room', 'status', 'created_at')
    search_fields = ('tenant__user__username', 'room__room_name')
    list_filter = ('status',)


