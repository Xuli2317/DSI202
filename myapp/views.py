from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Booking
from .forms import RoomCreateForm, RoomForm, BookingForm, Booking, GuestBookingForm, RoomImage, RoomImageForm
from .models import CustomUser, Tenant, Landlord
from django.forms import modelformset_factory

def home1(request):
    return render(request, 'home.html')

def home(request):
    max_price = request.GET.get('max_price')
    min_price = request.GET.get('min_price')
    dorm_name = request.GET.get('dorm_name')
    description = request.GET.get('description')

    queryset = Room.objects.all()

    if max_price:
        queryset = queryset.filter(price__lte=max_price)  # Filter rooms with price <= max_price
    if min_price:
        queryset = queryset.filter(price__gte=min_price)  # Filter rooms with price >= min_price
    if dorm_name:
        queryset = queryset.filter(dorm_name__icontains=dorm_name)  # Filter rooms with dorm_name containing the input text
    if description:
        queryset = queryset.filter(description__icontains=description)  # Filter by description

    return render(request, 'home.html', {'rooms': queryset})

class RoomDetailView(DetailView):
    model = Room
    template_name = 'room_detail.html'
    context_object_name = 'room'

class RoomSearchView(ListView):
    model = Room
    template_name = 'room_search.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Room.objects.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(furniture__icontains=query)
        ) if query else Room.objects.all()

def all_rooms(request):
    rooms = Room.objects.all()
    return render(request, 'all_rooms.html', {'rooms': rooms})

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
            booking.save()
            return redirect('booking_complete', booking_id=booking.id)
    else:
        form = GuestBookingForm()

    return render(request, 'booking_form.html', {'form': form, 'room': room})

def room_create(request):
    if request.method == 'POST':
        room_form = RoomForm(request.POST)
        room_image_form = RoomImageForm(request.POST, request.FILES)

        if room_form.is_valid() and room_image_form.is_valid():
            room = room_form.save()  # บันทึกห้องใหม่

            # รับไฟล์ที่อัปโหลด
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')

            if image1:
                room_image1 = RoomImage(room=room, image=image1)
                room_image1.save()

            if image2:
                room_image2 = RoomImage(room=room, image=image2)
                room_image2.save()

            return redirect('room_detail')  # เปลี่ยนไปหน้ารายละเอียดห้อง
    else:
        room_form = RoomForm()
        room_image_form = RoomImageForm()

    return render(request, 'room_create.html', {
        'room_form': room_form,
        'room_image_form': room_image_form
    })



