from django.contrib import admin
from .models import CustomUser, Tenant, Landlord, Room, Review, Booking, Admin

# Custom CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'role', 'is_active', 'date_joined')  # ใช้ 'username' แทน 'CustomUsername'
    search_fields = ('username', 'email', 'phone')  # ใช้ 'username' แทน 'CustomUsername'
    list_filter = ('role', 'is_active')

# Tenant Admin
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'budget', 'preferences')  # ใช้ 'user' แทน 'CustomUser'
    search_fields = ('user__username', 'user__email')  # ใช้ 'user' แทน 'CustomUser'

# Landlord Admin
@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')  # ใช้ 'user' แทน 'CustomUser'
    search_fields = ('user__username', 'user__email')  # ใช้ 'user' แทน 'CustomUser'

# Room Admin
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'landlord', 'price', 'location', 'available', 'created_at')
    search_fields = ('name', 'location', 'landlord__user__username')  # ใช้ 'landlord__user__username' แทน 'landlord__CustomUser__CustomUsername'
    list_filter = ('available', 'price')

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'room', 'rating', 'created_at')
    search_fields = ('tenant__user__username', 'room__name')  # ใช้ 'tenant__user__username' แทน 'tenant__CustomUser__CustomUsername'
    list_filter = ('rating',)

# Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'room', 'status', 'created_at')
    search_fields = ('tenant__user__username', 'room__name')  # ใช้ 'tenant__user__username' แทน 'tenant__CustomUser__CustomUsername'
    list_filter = ('status',)

# Admin Panel
@admin.register(Admin)
class CustomAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')  # ใช้ 'user' แทน 'CustomUser'
    search_fields = ('user__username', 'user__email')  # ใช้ 'user' แทน 'CustomUser'
