from game.engine import legal_moves
#from bots.base import Bot
from game.state import GameState
from game.moves import Move
from game.moves import EndTurn
from bots.base import Bot
import random
from game.engine import apply_move
from bots.value_bot import ValueBot
import pickle
import atexit


class Lethal_Bot(Bot):
    persistent_cache_loaded = False
    CACHE_FILE = "lethal_cache.pkl"
    move_cache={}

    @classmethod#REMEMBER TO CLEAR CACHE IF YOU ARE CHANGING KEY TUPLE OR ANYTHING THE EFFECTS LETHAL MECHANICS
    def save_cache(cls):
        if cls.persistent_cache_loaded:
            with open(cls.CACHE_FILE, "wb") as f:
                pickle.dump(cls.move_cache, f)

    @classmethod
    def load_cache(cls):
        if cls.persistent_cache_loaded:
            return
        cls.persistent_cache_loaded=True
        Lethal_Bot.load_cache()
        try:
            with open(cls.CACHE_FILE, "rb") as f:
                cls.move_cache = pickle.load(f)
            print(f"LOADED CACHE WITH {len(cls.move_cache)} ENTRIES")
        except FileNotFoundError:
            print("COULDNT FIND CACHE FILE")
            cls.move_cache={}

    def __init__(self, use_persistent_cache=True):#want different move trees for contaminated testing/differentdecks
        if use_persistent_cache:
            
            self.lethal_move_tree = self.move_cache
        else:
            self.lethal_move_tree = {}

        self.non_lethal_brain = ValueBot()

    def pick_move(self, state:GameState):
        #print("searching for lethal...")
        move = self.find_lethal(state)
        #print("done searching!")

        if move is None:
            return self.non_lethal_brain.pick_move(state)
        if len(move)==0:
            print("WARNING: lethal returned empty list — using fallback")
            return self.non_lethal_brain.pick_move(state)
        #print("implementing lethal")
        return move[0]


    def find_lethal(self, state:GameState)->list[Move]: 
        #print("new depth level in find_lethal")
        key = state.state_key()
        if key in self.lethal_move_tree:
            return self.lethal_move_tree[key]

        if state.players[1-state.current_player].hp<1:
            self.lethal_move_tree[key]=[]
            return []
        
        for moves in legal_moves(state):
            #print(moves)
            if isinstance(moves, EndTurn):
                continue

            new_state = apply_move(state,moves)
            result = self.find_lethal(new_state)

            if result is not None:
                #print("Found Lethal!!!")
                new_result=[moves]+result
                self.lethal_move_tree[key]=new_result
                return new_result
        self.lethal_move_tree[key]=None
        return None
        


atexit.register(Lethal_Bot.save_cache)#fires auto when py exits