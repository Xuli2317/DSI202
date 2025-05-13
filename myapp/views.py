from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Booking, CustomUser, Tenant, Landlord
from .forms import RoomCreateForm, RoomForm, BookingForm, GuestBookingForm, LandlordApplicationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import translation

def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

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
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, rooms_per_page)
    try:
        rooms = paginator.page(page)
    except:
        rooms = paginator.page(1)

    return render(request, 'home.html', {'rooms': rooms})

@login_required
def apply_landlord(request):
    if request.user.role == 'landlord':
        messages.error(request, "You are already a landlord.")
        return redirect('home')
    if request.method == 'POST':
        form = LandlordApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            Tenant.objects.filter(user=request.user).delete()
            request.user.role = 'landlord'
            request.user.save()
            landlord = form.save(commit=False)
            landlord.user = request.user
            landlord.is_verified = False
            landlord.save()
            messages.success(request, "Your landlord application has been submitted.")
            return redirect('home')
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
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.landlord = request.user.landlord_profile
            room.save()
            messages.success(request, "Room created successfully.")
            return redirect('home')
    else:
        form = RoomForm()
    return render(request, 'room_create.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Booking, Room
from .forms import GuestBookingForm

@login_required
def booking_create(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if not room.available:
        messages.error(request, "This room is not available.")
        return redirect('room_detail', pk=pk)
    if request.method == 'POST':
        form = GuestBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            try:
                tenant = request.user.tenant
                booking.tenant = tenant
                booking.full_name = request.user.get_full_name() or request.user.username
                booking.phone = getattr(tenant, 'phone', '')
                booking.email = request.user.email or ''
            except AttributeError:
                booking.full_name = form.cleaned_data['full_name']
                booking.phone = form.cleaned_data['phone']
                booking.email = request.user.email or ''
            if not booking.tenant and (not booking.full_name or not booking.phone):
                messages.error(request, "Either a tenant profile or guest details (full name and phone) must be provided.")
                return render(request, 'room_detail.html', {'form': form, 'room': room})
            booking.check_in = form.cleaned_data['check_in']
            booking.status = 'pending'
            booking.save()
            messages.success(request, "Booking created! Please proceed to payment.")
            return redirect('booking_payment', booking_id=booking.id)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = GuestBookingForm()
    return render(request, 'room_detail.html', {'form': form, 'room': room})

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
    context = {'user': user}
    if user.role == 'tenant':
        try:
            bookings = Booking.objects.filter(tenant=user.tenant)
        except Tenant.DoesNotExist:
            bookings = Booking.objects.filter(email=user.email)
        context['bookings'] = bookings
    elif user.role == 'landlord':
        bookings = Booking.objects.filter(room__landlord=user.landlord_profile)
        rooms = Room.objects.filter(landlord=user.landlord_profile)
        context['bookings'] = bookings
        context['rooms'] = rooms
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
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated successfully.")
            return redirect('profile')
    else:
        form = RoomForm(instance=room)
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