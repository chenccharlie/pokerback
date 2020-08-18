from pokerback.poker.objects import (
    PokerGames,
    GameMetadata,
    GameStatus,
    Game,
    PlayerGameState,
    PlayerTokens,
)
from pokerback.poker.utils import (
    get_random_cards,
    get_next_betting_idx,
    get_next_button_idx,
)
from pokerback.room.objects import GameType, SlotStatus
from pokerback.utils.redis import RedisLock


class PokerManager:
    def init_game(self, room, create_room_request):
        assert room.table_metadata.game_type == GameType.POKER
        assert room.poker_games == None

        small_blind = create_room_request.deep_get(
            "poker_request.small_blind", default=10
        )
        init_token = create_room_request.deep_get(
            "poker_request.init_token", default=1000
        )
        room.poker_games = PokerGames(
            game_metadata=GameMetadata(small_blind=small_blind, init_token=init_token)
        )
        room.save()
        return room

    def start_game(self, room):
        with RedisLock(room.room_uuid):
            poker_games = room.poker_games
            # assert no current games going on
            assert (
                len(poker_games.games) == 0
                or poker_games.games[-1].game_status == GameStatus.OVER
            )
            # assert at least 2 active players with enough tokens left are seated
            active_players = set()
            for slot in room.table_metadata.slots:
                player_id = slot.player_id
                if slot.slot_status == SlotStatus.ACTIVE:
                    active_players.add(player_id)
            assert len(active_players) > 1

            # If starting first game, assign default tokens to players
            if len(poker_games.games) == 0:
                for slot in room.table_metadata.slots:
                    player_id = slot.player_id
                    if player_id != None:
                        poker_games.players[player_id] = PlayerTokens(
                            player_id=player_id,
                            amount_available=poker_games.game_metadata.init_token,
                        )

            # Start creating new game
            # 1. random out the cards on the table and for each player
            cards = get_random_cards(5 + len(active_players) * 2)
            # 2. Set new button idx
            poker_games.game_metadata.button_idx = get_next_button_idx(
                room, poker_games.game_metadata.button_idx + 1
            )
            # 3. create Game object
            table_metadata = room.table_metadata.copy()
            game_metadata = poker_games.game_metadata.copy()
            game = Game(
                game_id=len(poker_games.games),
                table_metadata=table_metadata,
                game_metadata=game_metadata,
                table_cards=cards[0:5],
            )
            # 4. construct player states
            player_states = {}
            idx = 0
            for player_id in active_players:
                player_states[player_id] = PlayerGameState(
                    player_id=player_id,
                    cards=cards[5 + idx * 2 : 7 + idx * 2],
                    amount_available=poker_games.players[player_id].amount_available,
                )
                idx += 1
            game.player_states = player_states
            # 5. place small and big blinds
            slots = table_metadata.slots
            small_blind_idx = get_next_betting_idx(game, game_metadata.button_idx)
            small_blind_player_id = slots[small_blind_idx].player_id
            amount = min(
                game_metadata.small_blind,
                player_states[small_blind_player_id].amount_available,
            )
            player_states[small_blind_player_id].amount_betting = amount
            player_states[small_blind_player_id].amount_available -= amount

            big_blind_idx = get_next_betting_idx(game, small_blind_idx)
            big_blind_player_id = slots[big_blind_idx].player_id
            amount = min(
                game_metadata.small_blind * 2,
                player_states[big_blind_player_id].amount_available,
            )
            player_states[big_blind_player_id].amount_betting = amount
            player_states[big_blind_player_id].amount_available -= amount

            # Attach player states and next player id, save the game to game lists
            game.player_states = player_states
            game.next_player_id = slots[
                get_next_betting_idx(game, big_blind_idx)
            ].player_id
            poker_games.games.append(game)

            room.save()
            return room
