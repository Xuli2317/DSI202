from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import Room, Booking
from .forms import RoomCreateForm, RoomForm, BookingForm, Booking, GuestBookingForm
from .models import CustomUser, Tenant, Landlord

def home(request):
    return render(request, 'home.html')

class RoomListView(ListView):
    model = Room
    template_name = 'room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        max_price = self.request.GET.get('max_price')
        min_price = self.request.GET.get('min_price')
        dorm_name = self.request.GET.get('dorm_name')

        queryset = Room.objects.all()

        if max_price:
            queryset = queryset.filter(price__lte=max_price)  # Filter rooms with price <= max_price
        if min_price:
            queryset = queryset.filter(price__gte=min_price)  # Filter rooms with price >= min_price
        if dorm_name:
            queryset = queryset.filter(dorm_name__icontains=dorm_name)  # Filter rooms with dorm_name containing the input text

        return queryset

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

def some_error_page(request):
    return render(request, 'some_error_page.html')

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

# Room creation without login
def room_create(request):
    if request.method == 'POST':
        form = RoomCreateForm(request.POST, request.FILES)  # To support file uploads
        if form.is_valid():
            room = form.save(commit=False)
            room.landlord = None  # If no login, assume the user is an anonymous landlord, or handle it differently
            room.save()
            return redirect('room_list')  # Redirect to the list of rooms
    else:
        form = RoomCreateForm()
    return render(request, 'room_create.html', {'form': form})

# Add room functionality (still open for anyone)
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)

            # ไม่ต้องเชื่อมโยงกับ landlord (ห้องอาจไม่มีเจ้าของ)
            room.landlord = None  # หรือไม่ต้องกำหนดเลยหากไม่จำเป็น

            room.save()
            return redirect('room_list')  
        else:
            return redirect('some_error_page')  
    else:
        form = RoomForm()
    return render(request, 'add_room.html', {'form': form})


