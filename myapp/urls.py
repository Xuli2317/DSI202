# myapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.home, name='home'), 
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('search/', views.RoomSearchView.as_view(), name='room_search'),
    path('review/add/', views.ReviewCreateView.as_view(), name='add_review'),
    path('all-rooms/', views.all_rooms, name='all_rooms'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('error/', views.some_error_page, name='some_error_page'),
    
     # รายการห้อง
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('room/', views.RoomListView.as_view(), name='room_list'),
    path('room/<int:pk>/book/', views.booking_create, name='booking_create'),
    # รายละเอียดห้อง
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('room/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    # จองห้อง (POST)
    path('rooms/<int:pk>/book/', views.booking_create, name='booking_create'),
    path('room/<int:pk>/book/', views.booking_create, name='booking_create'),
    # หน้าแสดงสำเร็จ
    path('booking/<int:booking_id>/complete/', views.booking_complete, name='booking_complete'),
    
    # การเพิ่มห้อง
    path('room/add/', views.room_create, name='room_create'),
    path('add-room/', views.add_room, name='add_room'),
    path('booking/create/<int:pk>/', views.BookingCreateView.as_view(), name='booking_create'),
    path('booking/complete/<int:booking_id>/', views.booking_complete, name='booking_complete'),
]

