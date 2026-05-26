import random
from bots.base import Bot
from game.engine import legal_moves
from game.state import GameState
from game.moves import Move

class RandomBot(Bot):
    def pick_move(self, state: GameState) -> Move:
        return random.choice(legal_moves(state))