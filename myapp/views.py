from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Room, Review, Booking
from django.shortcuts import render

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

# Booking View
class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['room']
    template_name = 'booking_form.html'
    success_url = reverse_lazy('room_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.tenant_profile
        return super().form_valid(form)
    
def all_rooms(request):
    rooms = Room.objects.all()  # ดึงห้องทั้งหมดจากฐานข้อมูล
    return render(request, 'all_rooms.html', {'rooms': rooms})