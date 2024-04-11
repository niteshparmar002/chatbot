# chat/consumers.py
import json
from .models import *
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import os 
from django.conf import settings
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import warnings

def AIResponse(text):
    warnings.filterwarnings('ignore')
    "cohere api"
    "Google api"

    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_KEY 

    llm =ChatGoogleGenerativeAI(model='gemini-pro',convert_system_message_to_human=True)
    result = llm.invoke(text)

    # print(result.content)
    return result.content

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
        bot_res = AIResponse(message)

        dbsv = await self.save_chat(message, user, bot=False)
        await self.save_chat(bot_res, 3, bot=True)
        cid = dbsv['id']
        user_id = self.scope["user"].id
        usr = await sync_to_async(User.objects.get)(id=user_id)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, 'user':usr.username, 'id':cid, "bot_res":bot_res}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        bot_res1 = event["bot_res"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message,'user':event["user"],"bot_res":bot_res1}))

    @database_sync_to_async
    def save_chat(self, message, user, bot):
        if bot:
            cht = Chat.objects.create(sender=User.objects.get(id=user), channel=Channel.objects.get(id=self.room_name), message=message)
        else:
            cht = Chat.objects.create(sender=User.objects.get(id=user), channel=Channel.objects.get(id=self.room_name), message=message)
        return {"id":cht.id}
