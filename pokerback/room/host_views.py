from rest_framework import generics, status
from rest_framework.response import Response

from pokerback.room.managers import RoomManager
from pokerback.room.models import RoomModel
from pokerback.room.objects import GameType, RoomStatus
from pokerback.user.models import User
from pokerback.utils.authentication import HostAuthentication


class CreateRoomView(generics.CreateAPIView):
    authentication_classes = (HostAuthentication,)

    def post(self, request, *args, **kwargs):
        room_model = RoomManager.create_room(
            host_user=request.user, game_type=GameType.POKER,
        )
        room = room_model.load_room()
        return Response(room.to_json(), status=status.HTTP_200_OK)


class RetrieveRoomView(generics.RetrieveAPIView):
    authentication_classes = (HostAuthentication,)

    def get(self, request, *args, **kwargs):
        room_model = generics.get_object_or_404(
            RoomModel.objects, host_user=request.user, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()
        return Response(room.to_json(), status=status.HTTP_200_OK)
