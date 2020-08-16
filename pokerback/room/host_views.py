from rest_framework import generics

from pokerback.room.managers import RoomManager
from pokerback.room.models import RoomModel
from pokerback.room.objects import GameType, RoomStatus
from pokerback.room.services import HostRetrieveRoomResponse
from pokerback.user.models import User
from pokerback.utils.authentication import HostAuthentication
from pokerback.utils.views import BaseAPIView, BasicRequest


class CreateRoomView(BaseAPIView):
    authentication_classes = (HostAuthentication,)

    request_class = BasicRequest
    response_class = HostRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_model = RoomManager.create_room(
            host_user=self.request.user, game_type=GameType.POKER,
        )
        room = room_model.load_room()
        return HostRetrieveRoomResponse(room=room)


class RetrieveRoomView(BaseAPIView):
    authentication_classes = (HostAuthentication,)

    request_class = BasicRequest
    response_class = HostRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_model = generics.get_object_or_404(
            RoomModel.objects,
            host_user=self.request.user,
            room_status=RoomStatus.ACTIVE,
        )
        room = room_model.load_room()
        return HostRetrieveRoomResponse(room=room)
