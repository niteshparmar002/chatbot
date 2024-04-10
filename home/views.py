# chat/views.py
from django.shortcuts import render, HttpResponse
from .models import *

def index(request):
    channels = Channel.objects.all()
    return render(request, "chat/index.html", {'channels': channels})


def room(request, room_name):
    chats = Chat.objects.filter(channel__id=room_name)
    if request.user.is_authenticated:
        return render(request, "chat/room.html", {"room_name": room_name, "chats":chats})
    else:
        return HttpResponse("User is not authenticated")