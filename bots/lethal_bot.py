from game.engine import legal_moves
#from bots.base import Bot
from game.state import GameState
from game.moves import Move
from game.moves import EndTurn, Attack
from bots.base import Bot
from game.engine import apply_move
from bots.value_bot import ValueBot
import pickle
import atexit
from game.undo import undo_move


class Lethal_Bot(Bot):
    persistent_cache_loaded = False
    CACHE_FILE = "lethal_cache.pkl"
    move_cache={}

    @classmethod#REMEMBER TO CLEAR CACHE IF YOU ARE CHANGING KEY TUPLE OR ANYTHING THE EFFECTS LETHAL MECHANICS
    def save_cache(cls):
        if cls.persistent_cache_loaded:
            print("saving cache...")
            with open(cls.CACHE_FILE, "wb") as f:
                pickle.dump(cls.move_cache, f)
                

    @classmethod
    def load_cache(cls):
        if cls.persistent_cache_loaded:
            return
        cls.persistent_cache_loaded=True
        
        try:
            with open(cls.CACHE_FILE, "rb") as f:
                cls.move_cache = pickle.load(f)
            print(f"LOADED CACHE WITH {len(cls.move_cache)} ENTRIES")
        except FileNotFoundError:
            print("COULDNT FIND CACHE FILE")
            cls.move_cache={}

    def __init__(self, use_persistent_cache=True):#want different move trees for contaminated testing/differentdecks
        if use_persistent_cache:
            self.load_cache()
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
        
        opp = state.players[1-state.current_player]
        for mv in legal_moves(state):
            #print(mv)
            if (isinstance(mv, EndTurn) and opp.hp>opp.fatigue_counter) or (isinstance(mv,Attack) and opp.board[mv.target_index].taunt==False):#if the move is end turn or attacking a minion with no taunt
                continue

            tmp_undo = apply_move(state,mv)
            result = self.find_lethal(state)
            undo_move(state,tmp_undo)

            if result is not None:
                #print("Found Lethal!!!")
                new_result=[mv]+result
                self.lethal_move_tree[key]=new_result
                return new_result.copy()
        self.lethal_move_tree[key]=None
        return None
        


atexit.register(Lethal_Bot.save_cache)#fires auto when py exits