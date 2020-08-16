from pokerback.poker.objects import PokerGames, GameMetadata
from pokerback.room.objects import GameType


class PokerManager:
    def init_game(self, room, create_room_request):
        assert room.table_metadata.game_type == GameType.POKER
        assert room.poker_games == None

        small_blind = create_room_request.deep_get(
            "poker_request.small_blind", default=10
        )
        room.poker_games = PokerGames(
            game_metadata=GameMetadata(small_blind=small_blind,)
        )
        room.save()
        return room
