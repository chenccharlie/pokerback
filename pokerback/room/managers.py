import datetime
import random
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import generics

from pokerback.poker.managers import PokerManager
from pokerback.room.models import RoomModel
from pokerback.room.objects import RoomStatus, GameType, SlotStatus
from pokerback.utils.redis import RedisLock


def get_new_game_key():
    return "".join([chr(ord("A") + random.randint(0, 25)) for x in range(5)])


def get_game_manager(game_type):
    game_managers = {
        GameType.POKER: PokerManager(),
    }
    return game_managers[game_type]


class RoomManager:
    def create_room(self, host_user, game_type, create_room_request):
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

            with RedisLock(room_uuid):
                room = room_model.init_room(create_room_request)
                get_game_manager(game_type).init_game(room, create_room_request)
        return room_model

    def close_room(self, host_user):
        with transaction.atomic():
            room_model = generics.get_object_or_404(
                RoomModel.objects, host_user=host_user, room_status=RoomStatus.ACTIVE,
            )

            room = room_model.load_room()
            with RedisLock(room.room_uuid):
                room.room_status = RoomStatus.CLOSED
                room_record = room.to_json_str()
                room.delete()

            room_model.room_record = room_record
            room_model.room_status = RoomStatus.CLOSED
            room_model.closed_at = datetime.datetime.now()
            room_model.save()

    def sit_player(self, room, player, slot_idx):
        with RedisLock(room.room_uuid):
            original_state = None
            for slot in room.table_metadata.slots:
                if slot.player_id == player.uuid:
                    original_state = slot.slot_status
                    slot.player_id = None
                    slot.player_name = None
                    slot.slot_status = SlotStatus.EMPTY
            if slot_idx >= room.table_metadata.max_slots:
                raise ValidationError("Slot out of range.")
            if room.table_metadata.slots[slot_idx].slot_status != SlotStatus.EMPTY:
                raise ValidationError("Slot already filled.")

            room.table_metadata.slots[slot_idx].player_id = player.uuid
            room.table_metadata.slots[slot_idx].player_name = player.name
            room.table_metadata.slots[slot_idx].slot_status = (
                original_state or SlotStatus.ACTIVE
            )
            room.save()
            return room
