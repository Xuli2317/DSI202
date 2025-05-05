from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Booking
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['dorm_name', 'room_name', 'location', 'price', 'furniture', 'description', 'size']

    # ตรวจสอบให้ฟิลด์ `size` แสดงขึ้นมาในฟอร์ม
    size = forms.FloatField(required=True, label="Room Size")


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['dorm_name', 'room_name', 'price', 'location', 'description', 'image', 'size']
        widgets = {
            'dorm_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Dorm Name'
            }),
            'room_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Room Name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Price'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Location'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Room Description',
                'rows': 4
            }),
            'size': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Room Size (in sq. meters)',
                'step': '0.1'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg bg-white'
            }),
        }



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(available=True) 

    def save(self, commit=True):
        booking = super().save(commit=False)
        # ถ้าผู้ใช้ล็อกอินเป็น tenant กำหนด tenant
        if self.request and self.request.user.is_authenticated and hasattr(self.request.user, 'tenant_profile'):
            booking.tenant = self.request.user.tenant_profile
        if commit:
            booking.save()
        return booking
    
class GuestBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['full_name', 'phone']