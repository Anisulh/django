from django.db import models
import string
import random
import uuid


def code_generator():
    length = 6
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choice(chars) for _ in range(length))
        if Room.objects.filter(code=code).count() == 0:
            break
    return code


# Create your models here.


class Guest(models.Model):
    guest_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(null=False, max_length=50)
    host = models.BooleanField(blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Room(models.Model):
    code = models.CharField(
        max_length=6,
        default=code_generator,
        unique=True,
        primary_key=True,
        editable=False,
    )
    name = models.CharField(null=False, max_length=50)
    host_id = models.CharField(max_length=50, unique=True)
    guest_controller = models.BooleanField(null=False, default=False)
    guest = models.ManyToManyField(Guest, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_guest_count(self):
        return self.guest.count()

    def join(self, user):
        self.guest.add(user)
        self.save()

    def leave(self, user):
        self.guest.remove(user)
        self.save()

    def __str__(self):
        return f"{self.name}, {self.code} ({self.get_guest_count()})"


class Message(models.Model):
    user = models.ForeignKey(Guest, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.nickname}: {self.content} [{self.timestamp}]"
