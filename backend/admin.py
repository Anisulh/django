from django.contrib import admin
from backend.models import Room, Guest, Message

# Register your models here.
admin.site.register(Room)
admin.site.register(Guest)
admin.site.register(Message)