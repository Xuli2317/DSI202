# myapp/urls.py

from django.urls import path
from . import views
urlpatterns = [
    path('room/<int:pk>/book/', views.BookingCreateView.as_view(), name='booking_create'),
    path('', views.home, name='home'), 
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('search/', views.RoomSearchView.as_view(), name='room_search'),
    path('review/add/', views.ReviewCreateView.as_view(), name='add_review'),
    path('booking/add/', views.BookingCreateView.as_view(), name='add_booking'),
    path('all-rooms/', views.all_rooms, name='all_rooms'),
]
