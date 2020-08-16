from rest_framework import generics, status
from rest_framework.response import Response

from pokerback.room.models import RoomModel
from pokerback.room.objects import RoomStatus


class RetrieveRoomView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        room_key = request.query_params.get("room_key", "")
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()
        return Response(room.to_json(), status=status.HTTP_200_OK)
