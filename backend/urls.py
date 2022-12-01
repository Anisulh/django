
from django.urls import path
from .views import guest_view, room_view
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('guest', guest_view.GuestView),
    path('room', room_view.RoomView),
    path('room/<str:room_code>', room_view.SpecificRoomView),
]

urlpatterns = format_suffix_patterns(urlpatterns)
