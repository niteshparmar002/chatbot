# chat/consumers.py
import json
from .models import *
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = text_data_json["user"]

        dbsv = await self.save_chat(message, user)
        cid = dbsv['id']
        user_id = self.scope["user"].id
        usr = await sync_to_async(User.objects.get)(id=user_id)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, 'user':usr.username, 'id':cid}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message,'user':event["user"]}))

    @database_sync_to_async
    def save_chat(self, message, user):
        cht = Chat.objects.create(sender=User.objects.get(id=user), channel=Channel.objects.get(id=self.room_name), message=message)
        return {"id":cht.id}