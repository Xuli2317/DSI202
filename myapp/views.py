from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Booking, CustomUser, Tenant, Landlord
from .forms import RoomForm, BookingForm, LandlordApplicationForm, TenantProfileForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from myapp.allauth_forms import CustomSignupForm

def home(request):
    max_price = request.GET.get('max_price')
    min_price = request.GET.get('min_price')
    dorm_name = request.GET.get('dorm_name')
    description = request.GET.get('description')

    queryset = Room.objects.filter(available=True)
    if max_price:
        try:
            max_price = float(max_price)
            queryset = queryset.filter(price__lte=max_price)
        except ValueError:
            pass
    if min_price:
        try:
            min_price = float(min_price)
            queryset = queryset.filter(price__gte=min_price)
        except ValueError:
            pass
    if dorm_name:
        queryset = queryset.filter(dorm_name__icontains=dorm_name)
    if description:
        queryset = queryset.filter(description__icontains=description)

    rooms_per_page = 10
    page = request.GET.get('page', '1')
    paginator = Paginator(queryset, rooms_per_page)
    try:
        rooms = paginator.page(page)
    except:
        rooms = paginator.page(1)

    return render(request, 'home.html', {'rooms': rooms})

@login_required
def apply_landlord(request):
    if request.method == 'POST':
        user = request.user
        
        if user.role == 'landlord':
            messages.error(request, 'You are already a landlord.')
            return redirect('profile')
        
        form = LandlordApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                Tenant.objects.filter(user=user).delete()
                user.role = 'landlord'
                user.phone = form.cleaned_data['phone_number']
                user.save()
                
                landlord, created = Landlord.objects.get_or_create(user=user)
                landlord.phone_number = form.cleaned_data['phone_number']
                landlord.dorm_name = form.cleaned_data['dorm_name']
                landlord.bank_name = form.cleaned_data['bank_name']
                landlord.bank_account_number = form.cleaned_data['bank_account_number']
                landlord.account_holder_name = form.cleaned_data['account_holder_name']
                landlord.save()
                
                landlord_group, _ = Group.objects.get_or_create(name='Landlord')
                user.groups.clear()
                user.groups.add(landlord_group)
                
                messages.success(request, 'Your application has been submitted and you are now a Landlord.')
                return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LandlordApplicationForm()
    
    return render(request, 'apply_landlord.html', {'form': form})

class RoomDetailView(DetailView):
    model = Room
    template_name = 'room_detail.html'
    context_object_name = 'room'

class RoomSearchView(ListView):
    model = Room
    template_name = 'room_search.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = Room.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(room_name__icontains=query) |
                Q(location__icontains=query) |
                Q(description__icontains=query)
            )
        if self.request.GET.get('table'):
            queryset = queryset.filter(table_count__gt=0)
        if self.request.GET.get('bed'):
            queryset = queryset.filter(bed_count__gt=0)
        if self.request.GET.get('chair'):
            queryset = queryset.filter(chair_count__gt=0)
        return queryset

def all_rooms(request):
    rooms = Room.objects.filter(available=True)
    paginator = Paginator(rooms, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'all_rooms.html', {'page_obj': page_obj})

def booking_complete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_complete.html', {'booking': booking})

@login_required
def room_create(request):
    if request.user.role != 'landlord':
        messages.error(request, "Only landlords can create rooms.")
        return redirect('home')
    
    try:
        landlord_profile = request.user.landlord_profile
    except Landlord.DoesNotExist:
        messages.error(request, "Landlord profile not found. Please apply as a landlord first.")
        return redirect('apply_landlord')

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            room = form.save(commit=False)
            room.landlord = landlord_profile
            if Room.objects.filter(landlord=landlord_profile, dorm_name=room.dorm_name, room_name=room.room_name).exists():
                form.add_error('room_name', "A room with this name already exists in this dorm.")
                return render(request, 'room_create.html', {'form': form})
            room.save()
            messages.success(request, "Room created successfully.")
            return redirect('profile')
    else:
        form = RoomForm(user=request.user)
    return render(request, 'room_create.html', {'form': form})

def booking_create(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if not room.available:
        messages.error(request, "This room is not available for booking.")
        return redirect('room_detail', pk=room_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            if request.user.is_authenticated and request.user.role == 'tenant':
                try:
                    booking.tenant = request.user.tenant
                    booking.email = request.user.email
                    booking.phone = request.user.phone or form.cleaned_data['phone']
                    booking.full_name = request.user.username
                except Tenant.DoesNotExist:
                    messages.error(request, "Tenant profile not found. Please complete your profile.")
                    return render(request, 'room_detail.html', {'room': room, 'form': form})
            else:
                booking.full_name = form.cleaned_data['full_name']
                booking.phone = form.cleaned_data['phone']
                booking.email = form.cleaned_data.get('email', '')

            booking.check_in = form.cleaned_data['check_in']
            try:
                booking.clean()
                booking.save()
                
                if room.landlord and room.landlord.user.email:
                    subject = f"New Booking for {room.dorm_name} - {room.room_name}"
                    message = (
                        f"Dear {room.landlord.user.username},\n\n"
                        f"A new booking has been made for your room: {room.dorm_name} - {room.room_name}.\n"
                        f"Tenant: {booking.full_name or booking.tenant.user.username}\n"
                        f"Check-in: {booking.check_in}\n"
                        f"Check-out: {booking.check_out}\n"
                        f"Status: {booking.status.title()}\n\n"
                        f"Please review and confirm the booking in your profile."
                    )
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [room.landlord.user.email],
                        fail_silently=True,
                    )

                messages.success(request, "Booking created successfully!")
                return redirect('booking_complete', booking_id=booking.id)
            except ValidationError as e:
                form.add_error(None, e)
        return render(request, 'room_detail.html', {'room': room, 'form': form})
    else:
        form = BookingForm(initial={'check_in': date.today()})
    return render(request, 'room_detail.html', {'room': room, 'form': form})

@login_required
def booking_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, tenant__user=request.user, status='pending')
    return render(request, 'payment.html', {'booking': booking})

@login_required
def booking_payment_confirm(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, tenant__user=request.user, status='pending')
    if request.method == 'POST':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, "Payment confirmed! Your booking is now confirmed.")
        return redirect('profile')
    return redirect('booking_payment', booking_id=booking.id)

@login_required
def profile_view(request):
    user = request.user
    context = {'user': user, 'bookings': [], 'rooms': []}

    try:
        if user.role == 'tenant':
            tenant, created = Tenant.objects.get_or_create(user=user, defaults={'budget': 0})
            context['bookings'] = Booking.objects.filter(tenant=tenant).select_related('room')
            context['tenant_form'] = TenantProfileForm(instance=tenant, user=user)
        elif user.role == 'landlord':
            landlord_profile = user.landlord_profile
            context['bookings'] = Booking.objects.filter(room__landlord=landlord_profile).select_related('room', 'tenant__user')
            context['rooms'] = Room.objects.filter(landlord=landlord_profile)
    except (Tenant.DoesNotExist, Landlord.DoesNotExist):
        messages.error(request, "Profile not found. Please complete your profile setup.")
    
    return render(request, 'profile.html', context)

@login_required
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user.role != 'landlord' or booking.room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to confirm this booking.")
        return redirect('profile')
    booking.status = 'confirmed'
    booking.save()
    messages.success(request, "Booking confirmed successfully.")
    return redirect('profile')

@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user.role == 'landlord' and booking.room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('profile')
    if request.user.role == 'tenant' and booking.tenant != request.user.tenant:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('profile')
    booking.status = 'canceled'
    booking.save()
    messages.success(request, "Booking canceled successfully.")
    return redirect('profile')

@login_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user.role != 'landlord' or room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to edit this room.")
        return redirect('profile')
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully.")
            return redirect('profile')
    else:
        form = RoomForm(instance=room, user=request.user)
    return render(request, 'room_edit.html', {'form': form, 'room': room})

@login_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.user.role != 'landlord' or room.landlord != request.user.landlord_profile:
        messages.error(request, "You are not authorized to delete this room.")
        return redirect('profile')
    room.delete()
    messages.success(request, "Room deleted successfully.")
    return redirect('profile')

@login_required
def profile_edit(request):
    if request.user.role != 'tenant':
        messages.error(request, "Only tenants can edit tenant profiles.")
        return redirect('profile')
    
    try:
        tenant = request.user.tenant
    except Tenant.DoesNotExist:
        tenant = Tenant.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = TenantProfileForm(request.POST, instance=tenant, user=request.user)
        if form.is_valid():
            request.user.email = request.POST.get('email', request.user.email)
            request.user.phone = request.POST.get('phone', request.user.phone)
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TenantProfileForm(instance=tenant, user=request.user)
    
    return render(request, 'profile.html', {'form': form})

@login_required
def landlord_profile_edit(request):
    if request.user.role != 'landlord':
        messages.error(request, "Only landlords can edit landlord profiles.")
        return redirect('profile')
    
    try:
        landlord = request.user.landlord_profile
    except Landlord.DoesNotExist:
        messages.error(request, "Landlord profile not found.")
        return redirect('profile')
    
    if request.method == 'POST':
        form = LandlordApplicationForm(request.POST, instance=landlord)
        if form.is_valid():
            request.user.email = request.POST.get('email', request.user.email)
            request.user.phone = request.POST.get('phone_number', request.user.phone)
            request.user.save()
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LandlordApplicationForm(instance=landlord)
    
    return render(request, 'profile.html', {'form': form})