from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Booking, Landlord
from django.contrib.auth.forms import UserCreationForm
from .models import Landlord
from allauth.account.forms import SignupForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LandlordApplicationForm(forms.ModelForm):
    class Meta:
        model = Landlord
        fields = ['phone_number']

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
            'size', 'price', 'description', 'image'
        ]
        widgets = {
            'dorm_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Dorm Name'
            }),
            'room_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Room Name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Location'
            }),
            'table_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Tables'
            }),
            'bed_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Beds'
            }),
            'chair_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Chairs'
            }),
            'aircon_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Air Conditioners'
            }),
            'sofa_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Sofas'
            }),
            'wardrobe_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Wardrobes'
            }),
            'desk_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Desks'
            }),
            'tv_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of TVs'
            }),
            'refrigerator_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Refrigerators'
            }),
            'water_heater_count': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Number of Water Heaters'
            }),
            'size': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Room Size (in sq. meters)',
                'step': '0.1'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Price'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
                'placeholder': 'Room Description',
                'rows': 4
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg bg-white'
            }),
        }

class BookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(available=True)

    def save(self, commit=True):
        booking = super().save(commit=False)
        if self.request and self.request.user.is_authenticated and hasattr(self.request.user, 'tenant_profile'):
            booking.tenant = self.request.user.tenant_profile
        if commit:
            booking.save()
        return booking

    class Meta:
        model = Booking
        fields = ['room']

class GuestBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['full_name', 'phone', 'email', 'check_in', 'check_out']

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