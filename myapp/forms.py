from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Booking, Landlord, Tenant
from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError
from datetime import date
from django.shortcuts import render, redirect
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LandlordApplicationForm(forms.ModelForm):
    class Meta:
        model = Landlord
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border rounded-lg',
                'placeholder': 'Phone Number'
            }),
        }

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'dorm_name', 'room_name', 'location', 'price', 'description',
            'table_count', 'bed_count', 'chair_count', 'aircon_count','size'
        ]

    size = forms.FloatField(required=True, label="Room Size")

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'dorm_name', 'room_name', 'location', 
            'table_count', 'bed_count', 'chair_count', 'aircon_count',
            'sofa_count', 'wardrobe_count', 'desk_count', 'tv_count',
            'refrigerator_count', 'water_heater_count',
            'size', 'price', 'description', 'image','lease_duration_months' 
        ]
        widgets = {
            'dorm_name': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter dorm name'
            }),
            'room_name': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter room name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter location (e.g., near TU)'
            }),
            'table_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'bed_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'chair_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'aircon_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'sofa_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'wardrobe_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'desk_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'tv_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'refrigerator_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'water_heater_count': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': '0'
            }),
            'size': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter room size (e.g., 25.5)',
                'step': '0.1'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter price (e.g., 5000)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-5 py-3 rounded-lg border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Describe your room (e.g., amenities, features)',
                'rows': 4
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-5 py-3 rounded-lg border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm'
            }),
            'lease_duration_months': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter lease duration (e.g., 6)',
                'min': '1'
            }),
        }
        labels = {
            'table_count': 'Tables',
            'bed_count': 'Beds',
            'chair_count': 'Chairs',
            'aircon_count': 'Air Conditioners',
            'sofa_count': 'Sofas',
            'wardrobe_count': 'Wardrobes',
            'desk_count': 'Desks',
            'tv_count': 'TVs',
            'refrigerator_count': 'Refrigerators',
            'water_heater_count': 'Water Heaters',
            'dorm_name': 'Dorm Name',
            'room_name': 'Room Name',
            'location': 'Location',
            'size': 'Room Size (sq.m.)',
            'price': 'Price (THB)',
            'description': 'Description',
            'image': 'Room Image',
            'lease_duration_months': 'Lease Duration (Months)',
        }

class BookingForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="Email (for notifications)")

    class Meta:
        model = Booking
        fields = ['check_in', 'full_name', 'phone', 'email']
        widgets = {
            'check_in': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter your full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter your phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-5 py-3 rounded-full border border-gray-200 bg-[#f8f9fa] focus:outline-none focus:ring-2 focus:ring-[#4285f4] transition duration-300 shadow-sm placeholder-gray-400',
                'placeholder': 'Enter your email'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        full_name = cleaned_data.get('full_name')
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')

        if check_in and check_in < date.today():
            raise forms.ValidationError("Check-in date cannot be in the past.")
        
        # Require email for non-authenticated users
        if not self.instance.tenant and not email:
            raise forms.ValidationError({"email": "Email is required for guest bookings."})
        
        return cleaned_data


def booking_create(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            booking.user = request.user if request.user.is_authenticated else None
            # คำนวณ check-out date จาก lease_duration_months
            lease_months = room.lease_duration_months
            check_in = form.cleaned_data['check_in']
            check_out = check_in + datetime.timedelta(days=lease_months * 30)  # ประมาณ 30 วันต่อเดือน
            booking.check_out = check_out
            booking.full_name = form.cleaned_data['full_name']
            booking.phone = form.cleaned_data['phone']
            booking.save()
            messages.success(request, "Booking created successfully!")
            return redirect('booking_success')  # สมมติว่ามีหน้ายืนยันการจอง
        else:
            # ส่ง form ที่มีข้อผิดพลาดกลับไปยังเทมเพลต
            return render(request, 'room_detail.html', {'room': room, 'form': form})
    return redirect('room_detail', pk=room_id)

class CustomSignupForm(SignupForm):
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    def save(self, request):
        user = super().save(request)
        user.role = self.cleaned_data['role']
        user.save()
        return user

class TenantProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=15, required=False, label="Phone Number")

    class Meta:
        model = Tenant
        fields = ['budget', 'preferences']
        widgets = {
            'budget': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500'}),
            'preferences': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['phone'].initial = self.user.phone

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            self.user.phone = self.cleaned_data['phone']
            if commit:
                self.user.save()
        if commit:
            instance.save()
        return instance