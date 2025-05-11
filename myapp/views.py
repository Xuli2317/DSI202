from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Booking
from .forms import RoomCreateForm, RoomForm, BookingForm, Booking, GuestBookingForm, LandlordApplicationForm
from .models import CustomUser, Tenant, Landlord
from django.forms import modelformset_factory
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def home(request):
    max_price = request.GET.get('max_price')
    min_price = request.GET.get('min_price')
    dorm_name = request.GET.get('dorm_name')
    description = request.GET.get('description')

    queryset = Room.objects.filter(available=True)  # Start with rooms that are available

    # Filter by max_price if provided
    if max_price:
        try:
            max_price = float(max_price)
            queryset = queryset.filter(price__lte=max_price)
        except ValueError:
            # Handle invalid max_price input, if necessary
            pass

    # Filter by min_price if provided
    if min_price:
        try:
            min_price = float(min_price)
            queryset = queryset.filter(price__gte=min_price)
        except ValueError:
            # Handle invalid min_price input, if necessary
            pass

    # Filter by dorm_name if provided
    if dorm_name:
        queryset = queryset.filter(dorm_name__icontains=dorm_name)

    # Filter by description if provided
    if description:
        queryset = queryset.filter(description__icontains=description)

    # Pagination (Optional)
    rooms_per_page = 10
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, rooms_per_page)
    try:
        rooms = paginator.page(page)
    except PageNotAnInteger:
        rooms = paginator.page(1)
    except EmptyPage:
        rooms = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {'rooms': rooms})

@login_required
def apply_landlord(request):
    if request.user.role == 'landlord':
        messages.error(request, "You are already a landlord.")
        return redirect('home')

    if request.method == 'POST':
        form = LandlordApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # ลบโปรไฟล์ Tenant
            Tenant.objects.filter(user=request.user).delete()
            
            # เปลี่ยน role เป็น landlord
            request.user.role = 'landlord'
            request.user.save()
            
            # สร้างโปรไฟล์ Landlord
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

        # Furniture filters
        if self.request.GET.get('table'):
            queryset = queryset.filter(table_count__gt=0)
        if self.request.GET.get('bed'):
            queryset = queryset.filter(bed_count__gt=0)
        if self.request.GET.get('chair'):
            queryset = queryset.filter(chair_count__gt=0)

        return queryset

def all_rooms(request):
    rooms = Room.objects.filter(available=True)  # เริ่มจากเฉพาะห้องที่ available=True
    # rooms = Room.objects.all()  # ดึงห้องทั้งหมด
    paginator = Paginator(rooms, 8)  # จำนวนห้องต่อหน้า
    page_number = request.GET.get('page')  # รับหมายเลขหน้าจาก query parameter
    page_obj = paginator.get_page(page_number)  # สร้างหน้า

    # ส่งข้อมูลไปที่เทมเพลต
    return render(request, 'all_rooms.html', {'page_obj': page_obj})

def booking_complete(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_complete.html', {'booking': booking})


def booking_create(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        form = GuestBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room

            if request.user.is_authenticated:
                try:
                    tenant = request.user.tenant
                    booking.tenant = tenant
                    booking.full_name = request.user.get_full_name()
                    booking.phone = request.user.phone
                    booking.email = request.user.email
                except Tenant.DoesNotExist:
                    messages.error(request, "Only tenants can book rooms.")
                    return redirect('home')

            booking.save()
            messages.success(request, "Booking successful!")
            return redirect('booking_success')
    else:
        if request.user.is_authenticated:
            form = GuestBookingForm(initial={
                'full_name': request.user.get_full_name(),
                'phone': request.user.phone,
                'email': request.user.email,
            })
        else:
            form = GuestBookingForm()

    return render(request, 'booking_form.html', {'form': form, 'room': room})


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

def profile_view(request):
    return render(request, 'profile.html') 


@login_required
def quick_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    try:
        tenant = request.user.tenant
    except Tenant.DoesNotExist:
        messages.error(request, "Only tenants can book rooms.")
        return redirect('home')

    if request.method == 'POST':
        booking = Booking.objects.create(
            room=room,
            tenant=tenant,
            full_name=request.user.get_full_name(),
            phone=request.user.phone,
            email=request.user.email,
            status='pending'
        )
        messages.success(request, "Booking successful!")
        return redirect('booking_complete', booking_id=booking.id)

    return redirect('room_detail', pk=room_id)
