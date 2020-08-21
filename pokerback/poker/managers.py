from pokerback.poker.objects import (
    Action,
    ActionType,
    PokerGames,
    GameMetadata,
    GameStage,
    GameStatus,
    Game,
    PlayerGameState,
    PlayerTokens,
    PlayerStateResponse,
)
from pokerback.poker.utils import (
    get_random_cards,
    get_next_button_idx,
    get_player_min_bet,
    handle_game_over_player_update,
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
            # assert at least 2 active players are seated
            active_players = room.table_metadata.get_active_players()
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
            small_blind_idx = game.get_next_betting_idx(game_metadata.button_idx)
            small_blind_player_id = slots[small_blind_idx].player_id
            amount = min(
                game_metadata.small_blind,
                player_states[small_blind_player_id].amount_available,
            )
            player_states[small_blind_player_id].bet(amount)

            big_blind_idx = game.get_next_betting_idx(small_blind_idx)
            big_blind_player_id = slots[big_blind_idx].player_id
            amount = min(
                game_metadata.small_blind * 2,
                player_states[big_blind_player_id].amount_available,
            )
            player_states[big_blind_player_id].bet(amount)

            # Attach player states and next player id, save the game to game lists
            game.player_states = player_states
            game.next_player_id = slots[
                game.get_next_betting_idx(big_blind_idx)
            ].player_id
            poker_games.games.append(game)

            room.save()
            return room

    def handle_player_action(self, room, player_id, action_obj):
        with RedisLock(room.room_uuid):
            # assert game is playing
            assert (
                len(room.poker_games.games) > 0
                and room.poker_games.games[-1].game_status == GameStatus.PLAYING
            )
            game = room.poker_games.games[-1]
            # assert waiting for this player's action
            assert game.next_player_id == player_id

            player_states = game.player_states

            # Find out the min bets needed for the player
            min_bet = get_player_min_bet(player_states, player_id)

            # Extract and handle action
            poker_action = action_obj.poker_action
            if poker_action.action_type == ActionType.FOLD:
                # 1. Handle fold
                assert min_bet > 0
                player_states[player_id].fold()
            elif poker_action.action_type == ActionType.CHECK:
                # 2. Handle check
                assert min_bet == 0
            elif poker_action.action_type == ActionType.BET:
                # 3. Handle bet
                assert poker_action.amount_bet >= min_bet
                player_states[player_id].bet(poker_action.amount_bet)
            else:
                raise Exception("Invalid Choice")

            # Record player action
            game.actions.append(
                Action(
                    player_id=player_id,
                    game_stage=game.stage,
                    action_type=poker_action.action_type,
                    amount_bet=poker_action.amount_bet,
                )
            )

            # Check if game is over or stage is complete
            if game.is_folding():
                # Fold the game
                game.handle_fold()
            elif game.should_show_hand():
                # Advance to SHOW_HAND stage
                game.advance_stage(next_stage=GameStage.SHOW_HAND)
            elif game.is_stage_complete():
                # Advance to next stage
                game.advance_stage()
            else:
                # Advance to next player
                slots = game.table_metadata.slots
                game.next_player_id = slots[
                    game.get_next_betting_idx(game.get_player_idx(player_id))
                ].player_id

            if game.game_status == GameStatus.OVER:
                # Handle over game processes
                handle_game_over_player_update(room.poker_games.players, game)

            # Save and return room
            room.save()
            return room

    def fill_player_response(self, response, room, player_id):
        if room.poker_games == None or len(room.poker_games.games) == 0:
            return
        game = room.poker_games.games[-1]

        player_state = game.player_states[player_id]
        player_state_response = PlayerStateResponse(
            cards=player_state.cards,
            amount_available=player_state.amount_available,
            amount_betting=player_state.amount_betting,
            total_betting=player_state.total_betting,
            player_status=player_state.player_status,
            game_status=game.game_status,
            is_your_turn=(game.next_player_id == player_id),
            min_bet=get_player_min_bet(game.player_states, player_id),
        )
        response.poker_state = player_state_response
