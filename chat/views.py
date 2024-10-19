from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, Message
# from .serializers import ChatRoomSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_rooms(request):
    customer = request.user  # Get the current logged-in user
    rooms = ChatRoom.objects.filter(customer=customer)

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
