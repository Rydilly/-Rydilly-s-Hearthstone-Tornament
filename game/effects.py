from game.cards import CardName 
from game.state import GameState,PlayerState
from typing import Callable
from game.undo import Op as UndoOp
from game.undo import kill_minion

#adds a type sig to funcs without heavy overhead of abstract classes
EffectFn = Callable[[GameState,int,list],None]

START_OF_TURN:dict[CardName,EffectFn] = {}


#####################################       EFFECT FUNCTIONS
#START OF TURN BATTLECRIES
def _doomsayer_fn(state:GameState, owner_idx:int, undo:list):
    """kills all minions mutating state and undo"""

    #I reversed to save indices 
    for mn_idx in reversed(range(len(state.players[0].board))):
        kill_minion(state,0,mn_idx,undo)#kill minion appends to undo
    for mn_idx in reversed(range(len(state.players[1].board))):
        kill_minion(state,1,mn_idx,undo)

#Instant BattleCries
def _alexstraza_guardian_of_life_fn(state:GameState,owner_idx,undo:list):
    cur_player:PlayerState = state.players[owner_idx]
    undo.append((UndoOp.SET_PLAYER_HP,owner_idx,cur_player.hp))
    cur_player.hp=15
    undo.append((UndoOp.SET_ALEXSTRASZA_GUARDIAN_OF_LIFE_CHARGES,owner_idx,cur_player.alexstrasza_guardian_of_life_charges))
    cur_player.alexstrasza_guardian_of_life_charges+=1


###################################         EFFECT LIBRARY
INSTANT_BATTLECRIES = {CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE:_alexstraza_guardian_of_life_fn,
               }

START_OF_TURN = {CardName.DOOMSAYER:_doomsayer_fn
                 }

DEATHRATTLES = {}

END_OF_TURN = {}


