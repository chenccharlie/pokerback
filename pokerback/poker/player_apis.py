from pokerback.poker.objects import ActionType
from pokerback.utils.baseobject import BaseObject


class PokerAction(BaseObject):
    action_type: ActionType
    amount_bet: int = 0

    def validate(self):
        if self.action_type == ActionType.BET:
            assert self.amount_bet > 0
        else:
            assert self.amount_bet == 0
