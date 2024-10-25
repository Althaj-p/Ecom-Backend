from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, Message
from django.db.models import Q
# from .serializers import ChatRoomSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_rooms(request):
    print('hai')
    user = request.user  # Get the current logged-in user
    rooms = ChatRoom.objects.filter(Q(customer=user)|Q(support_agent=user))

    # Add the last message to each room (if any)
    room_data = []
    for room in rooms:
        last_message = Message.objects.filter(room=room).order_by('-timestamp').first()
        room_data.append({
            'room_id': room.room_id,
            'support_agent': {'username': room.support_agent.email},
            'last_message': last_message.text if last_message else None,
        })

    return Response(room_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_messages(request,roomId):
    print('hai')
    # customer = request.user  # Get the current logged-in user
    # rooms = ChatRoom.objects.filter(customer=customer)
    messages = Message.objects.filter(room__room_id=roomId)

    # Add the last message to each room (if any)
    # room_data = []
    # for room in rooms:
    #     last_message = Message.objects.filter(room=room).order_by('-timestamp').first()
    #     room_data.append({
    #         'room_id': room.room_id,
    #         'support_agent': {'username': room.support_agent.email},
    #         'last_message': last_message.text if last_message else None,
    #     })
    message_list = [
        {
            'room_id':room.id,
            'sender':room.sender.id,
            'message':room.text
        }for room in messages
    ]

    return Response(message_list)
