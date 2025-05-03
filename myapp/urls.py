from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home page
    path('', views.home, name='home'), 

    # Room List and Room Detail pages
    path('rooms/', views.RoomListView.as_view(), name='room_list'),  
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'), 

    # Search page for rooms
    path('search/', views.RoomSearchView.as_view(), name='room_search'),  

    # Page to view all rooms
    path('all-rooms/', views.all_rooms, name='all_rooms'),


    # Error page
    path('error/', views.some_error_page, name='some_error_page'),

    # Room Booking URLs
    path('room/<int:pk>/book/', views.booking_create, name='booking_create'),
    path('booking/<int:booking_id>/complete/', views.booking_complete, name='booking_complete'),

    # Add room functionality
    path('room/add/', views.room_create, name='room_create'), 
    path('add-room/', views.add_room, name='add_room'),

    # Booking Create View (used for specific room booking)
    path('booking/complete/<int:booking_id>/', views.booking_complete, name='booking_complete'),

     # Other URLs
    path('room/<int:pk>/book/', views.booking_create, name='booking_create'),
]
