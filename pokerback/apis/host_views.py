from rest_framework import generics

from pokerback.apis.host_apis import (
    HostCreateRoomRequest,
    HostRetrieveRoomResponse,
)
from pokerback.room.managers import RoomManager
from pokerback.room.models import RoomModel
from pokerback.room.objects import GameType, RoomStatus
from pokerback.user.models import User
from pokerback.utils.authentication import HostAuthentication
from pokerback.utils.views import BaseGetView, BasePostView, BasicRequest, BasicResponse


class CreateRoomView(BasePostView):
    authentication_classes = (HostAuthentication,)

    request_class = HostCreateRoomRequest
    response_class = HostRetrieveRoomResponse

    def handle_request(self, request_obj):
        room_model = RoomManager().create_room(
            host_user=self.request.user,
            game_type=request_obj.game_type,
            create_room_request=request_obj,
        )
        room = room_model.load_room()
        return HostRetrieveRoomResponse(room=room)


class RetrieveRoomView(BaseGetView):
    authentication_classes = (HostAuthentication,)

    response_class = HostRetrieveRoomResponse

    def handle_request(self):
        room_model = generics.get_object_or_404(
            RoomModel.objects,
            host_user=self.request.user,
            room_status=RoomStatus.ACTIVE,
        )
        room = room_model.load_room()
        return HostRetrieveRoomResponse(room=room)


class CloseRoomView(BasePostView):
    authentication_classes = (HostAuthentication,)

    request_class = BasicRequest
    response_class = BasicResponse

    def handle_request(self, request_obj):
        RoomManager().close_room(host_user=self.request.user)
        return BasicResponse()
