from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # ✅ ตั้งให้หน้าแรกใช้ room_list ที่กรอง available=True
    path('', views.home, name='home'),

    # หน้ารายละเอียดห้อง
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),

    # หน้าค้นหาห้อง
    path('search/', views.RoomSearchView.as_view(), name='room_search'),

    # หน้าแสดงห้องทั้งหมด
    path('all-rooms/', views.all_rooms, name='all_rooms'),

    # การจอง
    path('room/<int:pk>/book/', views.booking_create, name='booking_create'),
    path('booking/<int:booking_id>/complete/', views.booking_complete, name='booking_complete'),
    path('booking/complete/<int:booking_id>/', views.booking_complete, name='booking_complete'),

    # เพิ่มห้องใหม่
    path('room/add/', views.room_create, name='room_create'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
