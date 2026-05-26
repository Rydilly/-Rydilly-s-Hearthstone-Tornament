from game.cards import CardName 
from game.state import GameState,PlayerState

#Instant BattleCries
def _doomsayer_fn(state:GameState, owner_idx):
    state.players[1].board=[]
    state.players[0].board=[]

#START OF TURN BATTLECRIES
def _alexstraza_guardian_of_life_fn(state:GameState,owner_idx):
    cur_player:PlayerState = state.players[owner_idx]
    cur_player.hp=15
    cur_player.alexstraza_guardian_of_life_charges+=1




INSTANT_BATTLECRIES = {CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE:_alexstraza_guardian_of_life_fn,
               }

START_OF_TURN = {CardName.DOOMSAYER:_doomsayer_fn
                 }

DEATHRATTLES = {}

END_OF_TURN = {}


