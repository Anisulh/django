from rest_framework import serializers
from .models import Room, Guest


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["guest_id", "guest_controller"]

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'





