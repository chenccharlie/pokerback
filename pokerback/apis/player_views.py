from rest_framework import generics

from pokerback.apis.player_apis import (
    PlayerRetrieveRoomRequest,
    PlayerRetrieveRoomResponse,
    PlayerJoinRoomRequest,
)
from pokerback.room.managers import RoomManager
from pokerback.room.models import RoomModel
from pokerback.room.objects import RoomStatus
from pokerback.utils.views import BaseAPIView


class RetrieveRoomView(BaseAPIView):
    request_class = PlayerRetrieveRoomRequest
    response_class = PlayerRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_key = request_obj.room_key
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()
        return PlayerRetrieveRoomResponse(room=room)


class JoinRoomView(BaseAPIView):
    request_class = PlayerJoinRoomRequest
    response_class = PlayerRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_key = request_obj.room_key
        slot_idx = request_obj.slot_idx
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()

        room = RoomManager().add_player(room, self.request.user, slot_idx)

        return PlayerRetrieveRoomResponse(room=room)
