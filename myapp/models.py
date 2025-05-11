from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

User = settings.AUTH_USER_MODEL

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')  # ค่าเริ่มต้นเป็น tenant

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True
    )

# Tenant Model
class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preferences = models.TextField(blank=True, null=True)

# Landlord Model
class Landlord(models.Model):
    user = models.OneToOneField('myapp.CustomUser', on_delete=models.CASCADE, related_name='landlord_profile')
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - Landlord'


# Room Model
class Room(models.Model):
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True) 
    dorm_name = models.CharField(max_length=255)
    room_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
     # เฟอร์นิเจอร์พร้อมจำนวน
    table_count = models.PositiveIntegerField(default=0, verbose_name="table_count")
    bed_count = models.PositiveIntegerField(default=0, verbose_name="bed_count")
    chair_count = models.PositiveIntegerField(default=0, verbose_name="chair_count")
    aircon_count = models.PositiveIntegerField(default=0, verbose_name="aircon_count")

    size = models.FloatField()

    description = models.TextField(blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dorm_name} - {self.room_name}"


# Booking Model
class Booking(models.Model):
    ROOM_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ]

    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    tenant = models.ForeignKey('Tenant', on_delete=models.CASCADE, null=True, blank=True) 
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)  
    check_in = models.DateField(null=True, blank=True)  
    check_out = models.DateField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ROOM_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Booking {self.id} for {self.room.room_name}"
    
    def clean(self):
        if not self.tenant and not (self.full_name and self.phone):
            raise ValidationError("Either a tenant or guest details (full_name and phone) must be provided.")


class Review(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comfort = models.TextField(blank=True)
    cleanliness = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.tenant.username} for {self.room.room_name}"

@receiver(post_save, sender=Booking)
def update_room_availability_on_booking_save(sender, instance, **kwargs):
    if instance.status in ['pending', 'confirmed']:
        instance.room.available = False
        instance.room.save()
    elif instance.status == 'canceled':
        # ถ้าไม่มี booking อื่นที่ pending หรือ confirmed อยู่
        other_active = Booking.objects.filter(
            room=instance.room, status__in=['pending', 'confirmed']
        ).exclude(id=instance.id).exists()
        if not other_active:
            instance.room.available = True
            instance.room.save()


@receiver(post_delete, sender=Booking)
def update_room_availability_on_booking_delete(sender, instance, **kwargs):
    other_active = Booking.objects.filter(
        room=instance.room, status__in=['pending', 'confirmed']
    ).exclude(id=instance.id).exists()
    if not other_active:
        instance.room.available = True
        instance.room.save()

@receiver(post_save, sender=CustomUser)
def create_profile_based_on_role(sender, instance, created, **kwargs):
    if instance.role == 'tenant':
        Tenant.objects.get_or_create(user=instance)
    elif instance.role == 'landlord':
        Landlord.objects.get_or_create(user=instance)
