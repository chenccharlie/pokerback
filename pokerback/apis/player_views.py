import uuid

from rest_framework import generics

from pokerback.apis.player_apis import (
    PlayerRetrieveRoomResponse,
    PlayerSigninRequest,
    PlayerSitRoomRequest,
)
from pokerback.room.managers import RoomManager
from pokerback.room.models import RoomModel
from pokerback.room.objects import RoomStatus
from pokerback.utils.authentication import PlayerSigninAuthentication
from pokerback.utils.views import BaseGetView, BasePostView, BasicRequest


class SigninView(BasePostView):
    authentication_classes = (PlayerSigninAuthentication,)

    request_class = PlayerSigninRequest
    response_class = PlayerRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_key = request_obj.room_key
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )

        if "uuid" not in self.request.session:
            self.request.session["uuid"] = str(uuid.uuid4())
        self.request.session["name"] = request_obj.name
        self.request.session["room_key"] = room_key

        room = room_model.load_room()
        return PlayerRetrieveRoomResponse(room=room)


class RetrieveRoomView(BaseGetView):
    response_class = PlayerRetrieveRoomResponse

    def handle_request(self):
        room_key = self.request.user.room_key
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()
        return PlayerRetrieveRoomResponse(room=room)


class SitRoomView(BasePostView):
    request_class = PlayerSitRoomRequest
    response_class = PlayerRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_key = self.request.user.room_key
        slot_idx = request_obj.slot_idx
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()

        room = RoomManager().sit_player(room, self.request.user, slot_idx)

        return PlayerRetrieveRoomResponse(room=room)
