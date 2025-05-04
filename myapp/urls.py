from django.urls import path
from . import views

urlpatterns = [
    # Home page (รวมฟอร์มค้นหาและผลลัพธ์)
    path('', views.home, name='home'),  # แสดงผลในหน้า home
    
    # Room List and Room Detail pages
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),  # รายละเอียดห้อง

    # Room Search page (ค้นหาห้อง)
    path('search/', views.RoomSearchView.as_view(), name='room_search'),  # ค้นหาห้อง
    
    # Page to view all rooms (แสดงทั้งหมด)
    path('all-rooms/', views.all_rooms, name='all_rooms'),  # แสดงห้องทั้งหมด

    # Room Booking URLs
    path('room/<int:pk>/book/', views.booking_create, name='booking_create'),  # จองห้อง
    path('booking/<int:booking_id>/complete/', views.booking_complete, name='booking_complete'),  # ยืนยันการจอง

    # Add room functionality
    path('room/add/', views.room_create, name='room_create'),  # เพิ่มห้อง
    path('add-room/', views.add_room, name='add_room'),  # เพิ่มห้อง

    # Booking Complete page
    path('booking/complete/<int:booking_id>/', views.booking_complete, name='booking_complete'),
]
