from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Room, Review, Booking
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import Booking, Room
from .forms import RoomCreateForm, Room, RoomForm
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
        dorm_name = self.request.GET.get('dorm_name')  # รับค่าชื่อหอ
        room_name = self.request.GET.get('room_name')  # รับค่าชื่อห้อง

        queryset = Room.objects.all()

        if max_price:
            queryset = queryset.filter(price__lte=max_price)  # กรองห้องพักที่ราคาไม่เกิน max_price
        if min_price:
            queryset = queryset.filter(price__gte=min_price)  # กรองห้องพักที่ราคาไม่ต่ำกว่า min_price

        if dorm_name:
            queryset = queryset.filter(dorm_name__icontains=dorm_name)  # กรองห้องพักที่มีชื่อหอเหมือนกับ dorm_name
        
        if room_name:
            queryset = queryset.filter(room_name__icontains=room_name)  # กรองห้องพักที่มีชื่อห้องเหมือนกับ room_name

        return queryset

class RoomDetailView(DetailView):
    model = Room
    template_name = 'room_detail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

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

# Review View
class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ['room', 'rating', 'comment']
    template_name = 'review_form.html'
    success_url = reverse_lazy('room_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.tenant_profile
        return super().form_valid(form)
    
def all_rooms(request):
    rooms = Room.objects.all()  # ดึงห้องทั้งหมดจากฐานข้อมูล
    return render(request, 'all_rooms.html', {'rooms': rooms})

def booking_complete(request, booking_id):
    # ดึงข้อมูลการจองที่มี booking_id
    booking = get_object_or_404(Booking, id=booking_id)
    
    return render(request, 'booking_complete.html', {'booking': booking})

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['room']
    template_name = 'booking_complete.html'
    
    def form_valid(self, form):
        form.instance.tenant = self.request.user.tenant_profile  # สมมติว่า tenant_profile เชื่อมกับ CustomUser
        booking = form.save()  # บันทึกการจอง
        
        # Redirect ไปยังหน้าจบการจองพร้อมกับแสดงรายละเอียดการจอง
        return redirect('booking_complete', booking_id=booking.id)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 👇 เพิ่มตรงนี้: สร้างโปรไฟล์ตาม role ที่เลือก
            if user.role == 'tenant':
                Tenant.objects.create(user=user, budget=0)  # หรือใส่ budget ตามฟอร์มก็ได้
            elif user.role == 'landlord':
                Landlord.objects.create(user=user)

            return redirect('login')  # ไปหน้า login หลังสมัครเสร็จ
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def some_error_page(request):
    return render(request, 'some_error_page.html')

@require_POST
@login_required
def booking_create(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if not request.user.is_authenticated:
        return redirect('login')  # ถ้ายังไม่ล็อกอินให้ไปที่ login

    if not hasattr(request.user, 'tenant_profile'):
        return redirect('some_error_page')  # หรือ error page ที่คุณมี

    booking = Booking.objects.create(
        room=room,
        tenant=request.user.tenant_profile
    )

    return redirect('booking_complete', booking_id=booking.id)


# View สำหรับกรอกข้อมูลห้องใหม่
@login_required
def room_create(request):
    if request.method == 'POST':
        form = RoomCreateForm(request.POST, request.FILES)  # เพื่อรองรับการอัปโหลดรูป
        if form.is_valid():
            room = form.save(commit=False)
            # เชื่อมโยงเจ้าของห้อง (landlord) กับผู้ใช้ที่ล็อกอิน
            room.landlord = request.user.landlord_profile  # เชื่อมโยงผู้ใช้งานที่ล็อกอินเป็นเจ้าของห้อง
            room.save()
            return redirect('room_list')  # Redirect ไปยังหน้าห้องทั้งหมด
    else:
        form = RoomCreateForm()
    return render(request, 'room_create.html', {'form': form})

@login_required
def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)

            # 👇 ตรวจสอบว่า user มี landlord_profile
            if hasattr(request.user, 'landlord_profile'):
                room.landlord = request.user.landlord_profile
                room.save()
                return redirect('room_list')
            else:
                return redirect('some_error_page')  # หรือแจ้งเตือนว่าไม่ใช่เจ้าของหอ
    else:
        form = RoomForm()
    return render(request, 'add_room.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            role = form.cleaned_data['role']
            if role == 'tenant':
                Tenant.objects.create(user=user, budget=0)
            elif role == 'landlord':
                Landlord.objects.create(user=user)

            return redirect('login')  # 👈 ไปหน้า login หลังสมัคร
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
