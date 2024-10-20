# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import ChatRoom, Message
# from accounts.models import User

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_id = self.scope['url_route']['kwargs']['room_id']
#         self.room_group_name = f'chat_{self.room_id}'

#         # Join the room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave the room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         sender_email = data['sender']

#         sender = await User.objects.get(email=sender_email)
#         room = await ChatRoom.objects.get(room_id=self.room_id)

#         # Save the message to the database
#         await Message.objects.create(room=room, sender=sender, text=message)

#         # Broadcast the message to the group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'sender': sender_email
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         sender = event['sender']

#         # Send the message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'sender': sender
#         }))


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import ChatRoom, Message
from accounts.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_email = data['sender']

        # Use sync_to_async to handle the ORM operations asynchronously
        sender = await sync_to_async(User.objects.get)(email=sender_email)
        room = await sync_to_async(ChatRoom.objects.get)(room_id=self.room_id)

        # Save the message to the database
        await sync_to_async(Message.objects.create)(room=room, sender=sender, text=message)

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_email
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
