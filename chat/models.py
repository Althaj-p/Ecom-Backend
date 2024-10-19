from django.db import models
from accounts.models import User

class ChatRoom(models.Model):
    room_id = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(User, related_name='customer_chats', on_delete=models.CASCADE)
    support_agent = models.ForeignKey(User, related_name='agent_chats', on_delete=models.CASCADE)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE,null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)