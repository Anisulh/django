import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Room, Guest
from urllib.parse import urlparse


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def create_chat(self, guest_id, message):
        room = Room.objects.get(pk=self.room_name)
        guest = Guest.objects.get(pk=guest_id)
        instance = Message.objects.create(user=guest, room=room, content=message)
        nickname = guest.nickname
        _id = instance.pk
        return {"_id": _id, "nickname": nickname}

    @database_sync_to_async
    def get_guest(self, guest_id):
        guest = Guest.objects.get(pk=guest_id)
        return guest.nickname

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # Send message to room group
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Send message to room group
        if "player" in text_data_json:
            _type = text_data_json["player"]["_type"]
            uri = text_data_json["player"]["uri"]
            position = text_data_json["player"]["position"]
            paused = text_data_json["player"]["paused"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "spotify_message",
                    "_type": _type,
                    "uri": uri,
                    "position": position,
                    "paused": paused,
                },
            )
        elif "connection" in text_data_json:
            guest = text_data_json["connection"]["guest_id"]
            nickname = await self.get_guest(guest)
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "connect_message", "guest": nickname},
            )
        else:
            message = text_data_json["message"]
            guest_id = text_data_json["guest_id"]
            data = await self.create_chat(guest_id, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "guest_id": guest_id,
                    "_id": data["_id"],
                    "nickname": data["nickname"],
                },
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        guest_id = event["guest_id"]
        _id = event["_id"]
        nickname = event["nickname"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": {
                        "_id": _id,
                        "guest_id": guest_id,
                        "nickname": nickname,
                        "message": message,
                    }
                }
            )
        )

    async def connect_message(self, event):
        guest = event["guest"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"connection": {"guest": guest}}))

    async def spotify_message(self, event):
        _type = event["_type"]
        uri = event["uri"]
        position = event["position"]
        paused = event["paused"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "spotify": {
                        "_type": _type,
                        "uri": uri,
                        "position": position,
                        "paused": paused,
                    }
                }
            )
        )
