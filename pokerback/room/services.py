from pokerback.room.models import Room
from pokerback.utils.baseobject import BaseObject


class PlayerRetrieveRoomRequest(BaseObject):
    room_key: str


class PlayerRetrieveRoomResponse(BaseObject):
    room: Room


class HostRetrieveRoomResponse(BaseObject):
    room: Room
