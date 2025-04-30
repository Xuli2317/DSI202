from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

User = settings.AUTH_USER_MODEL


class CustomUser(AbstractUser):
    # ลบ UUIDField ออก
    phone = models.CharField(max_length=15, blank=True, null=True)
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    )
    role = models.CharField(max_length=20, choices=[('tenant', 'Tenant'), ('landlord', 'Landlord')])
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # แก้ไขชื่อของ reverse accessor ที่ไม่ซ้ำกับ auth.User
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # แก้ไขชื่อของ reverse accessor ที่ไม่ซ้ำกับ auth.User
        blank=True
    )


# Tenant Model
class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preferences = models.TextField(blank=True, null=True)

class Landlord(models.Model):
    user = models.OneToOneField('myapp.CustomUser', on_delete=models.CASCADE, related_name='landlord_profile')
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - Landlord'

# Room Model
class Room(models.Model):
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name='rooms')
    
    dorm_name = models.CharField(max_length=255)  # 🏢 ชื่อหอพัก
    room_name = models.CharField(max_length=255)  # 🚪 ชื่อห้อง (หรือเลขห้อง)

    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    furniture = models.TextField()
    size = models.FloatField()
    description = models.TextField(blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dorm_name} - {self.room_name}"

# Review Model
class Review(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='reviews')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Booking Model
class Booking(models.Model):
    ROOM_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ROOM_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking {self.id} for {self.room.room_name} by {self.tenant.user.username}"

