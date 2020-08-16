import random
import uuid

from django.db import transaction

from pokerback.room.models import RoomModel
from pokerback.room.objects import RoomStatus


def get_new_game_key():
    return "".join([chr(ord("A") + random.randint(0, 25)) for x in range(5)])


class RoomManager:
    @classmethod
    def create_room(cls, host_user, game_type, **kwargs):
        with transaction.atomic():
            room_uuid = str(uuid.uuid4())
            room_key = get_new_game_key()

            room_model = RoomModel.objects.create(
                room_uuid=room_uuid,
                room_key=room_key,
                host_user=host_user,
                game_type=game_type,
                room_status=RoomStatus.ACTIVE,
            )

        room_model.init_room(**kwargs)
        return room_model
