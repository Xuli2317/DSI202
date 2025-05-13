from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('search/', views.RoomSearchView.as_view(), name='room_search'),
    path('all-rooms/', views.all_rooms, name='all_rooms'),
    path('room/<int:room_id>/book/', views.booking_create, name='booking_create'),
    path('booking/<int:booking_id>/complete/', views.booking_complete, name='booking_complete'),
    path('room/add/', views.room_create, name='room_create'),
    path('profile/', views.profile_view, name='profile'),
    path('accounts/', include('allauth.urls')),
    path('login/', lambda request: redirect('/accounts/google/login/'), name='login'),
    path('apply-landlord/', views.apply_landlord, name='apply_landlord'),
    path('booking/<int:pk>/confirm/', views.booking_confirm, name='booking_confirm'),
    path('booking/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('room/<int:pk>/edit/', views.room_edit, name='room_edit'),
    path('room/<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('booking/<int:booking_id>/payment/', views.booking_payment, name='booking_payment'),
    path('booking/<int:booking_id>/payment/confirm/', views.booking_payment_confirm, name='booking_payment_confirm'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)