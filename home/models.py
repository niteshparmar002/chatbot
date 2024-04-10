from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Channel(models.Model):
    employee = models.ManyToManyField(User)
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name
    
class Chat(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
        
    def __str__(self):
        return f'{self.sender} - {self.channel}'
