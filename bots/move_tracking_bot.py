from bots.base import Bot
from game.state import GameState
import pickle
import atexit
from game.engine import apply_move
from game.moves import Move, EndTurn
from bots.value_bot import ValueBot
from bots.opponent_model import OpponentModel

"""
CURRENT OBJ
1. TRACK OPPONENT
2.PLAYS IDENTICAL TO VALUEBOT
"""

class Move_Tracking_Bot(Bot):

    def __init__(self, use_persistent_cache=True):
        self.default_brain = ValueBot()
        self.eyes = OpponentModel()
        
    def pick_move(self, state):
        return self.default_brain.pick_move(state)
    
    def observe(self, state, move):
        self.eyes.observe(state, move)



if __name__=="__main__":
    from play import play_game
    
    bot = Move_Tracking_Bot()
    winner = play_game(bot, ValueBot())
    print(f"winner:{winner}")
    print(f"Played by Opponent: {dict(bot.eyes.played)}")
    print(f"Unseen by Opponent: {dict(bot.eyes.played)}")
    assert sum(bot.eyes.played.values())+sum(bot.eyes.unseen.values())==15