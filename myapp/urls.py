from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('search/', views.RoomSearchView.as_view(), name='room_search'),
    path('all-rooms/', views.all_rooms, name='all_rooms'),
    path('room/<int:pk>/book/', views.booking_create, name='booking_create'),
    path('booking/<int:booking_id>/complete/', views.booking_complete, name='booking_complete'),
    path('room/add/', views.room_create, name='room_create'),
    path('profile/', views.profile_view, name='profile'),
    path('choose-role/', views.choose_role, name='choose_role'),
    path('accounts/', include('allauth.urls')),
    path('login/', lambda request: redirect('/accounts/google/login/'), name='login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
