import uuid

from rest_framework import generics

from pokerback.apis.player_apis import (
    PlayerActionRequest,
    PlayerRetrieveRoomResponse,
    PlayerSigninRequest,
    PlayerSitRoomRequest,
)
from pokerback.room.managers import RoomManager, get_game_manager
from pokerback.room.models import RoomModel
from pokerback.room.objects import RoomStatus
from pokerback.utils.authentication import PlayerSigninAuthentication
from pokerback.utils.views import BaseGetView, BasePostView, BasicRequest, BasicResponse


class SigninView(BasePostView):
    authentication_classes = (PlayerSigninAuthentication,)

    request_class = PlayerSigninRequest
    response_class = BasicResponse

    def handle_request(self, request_obj):
        room_key = request_obj.room_key
        generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )

        if "uuid" not in self.request.session:
            self.request.session["uuid"] = str(uuid.uuid4())
        self.request.session["name"] = request_obj.name
        self.request.session["room_key"] = room_key

        return BasicResponse()


class RetrieveRoomView(BaseGetView):
    response_class = PlayerRetrieveRoomResponse

    def handle_request(self):
        room_key = self.request.user.room_key
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()
        return PlayerRetrieveRoomResponse.from_room(room=room, request=self.request)


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

        return PlayerRetrieveRoomResponse.from_room(room=room, request=self.request)


class PlayerActionView(BasePostView):
    request_class = PlayerActionRequest
    response_class = PlayerRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_key = self.request.user.room_key
        room_model = generics.get_object_or_404(
            RoomModel.objects, room_key=room_key, room_status=RoomStatus.ACTIVE
        )
        room = room_model.load_room()
        room = get_game_manager(room.table_metadata.game_type).handle_player_action(
            room, self.request.user.uuid, request_obj
        )

        return PlayerRetrieveRoomResponse.from_room(room=room, request=self.request)
