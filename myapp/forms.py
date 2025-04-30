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
        fields = ['dorm_name', 'room_name', 'location', 'price', 'furniture', 'description', 'image', 'size']

    # ตรวจสอบให้ฟิลด์ `size` แสดงขึ้นมาในฟอร์ม
    size = forms.FloatField(required=True, label="Room Size")


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['dorm_name', 'room_name', 'price', 'location', 'description', 'image']
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
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-black rounded-lg',
            }),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)  

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role'] 