from collections import Counter

"""
watches games and stores when a game state wins or loses
"""
import pickle
import atexit
"""
In the future i wish to cache a max damage from a board state to allow more reuse. sadly a lot of info that isnt usually needed needs to be included because it can mean lethal. It might be better to hard code those spots later.
"""

class Watcher():
    persistent_cache_loaded = False
    CACHE_FILE = "State_Rate.pkl"
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

    def __init__(self, use_persistent_cache=True):#want different move trees for contaminated testing/different decks
        if use_persistent_cache:
            self.load_cache()
            self.state_log = self.move_cache
        else:
            self.lethal_move_tree = {}


        


atexit.register(Watcher.save_cache)#fires auto when py exits