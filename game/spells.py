from game.moves import Target,Move,FriendlyHero,EnemyHero,FriendlyMinion,EnemyMinion
from game.state import GameState, PlayerState, Minion
from game.undo import Op as UndoOp
from game.helpers import kill_minion, draw_card, heal, deal_damage
import random
from game.cards import CardName

def _flash_heal(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    heal(state,my_idx,target,state.players[my_idx].heal_power(heal),undo)


def _holy_smite(state:GameState, my_idx:int, target:EnemyMinion|FriendlyMinion, undo:list[Move]):
    deal_damage(state,my_idx,target,state.players[my_idx].spell_amp(3),undo)


def _mend(state:GameState, my_idx:int, target:EnemyMinion, undo:list[Move]):
    me=state.players[my_idx]
    opp=state.players[1-my_idx]
    heal(state,my_idx,target,me.heal_power(opp.board[target.index].max_health),undo)


def _power_word_barrier(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("power_word_barrier effect not implemented yet")

def _power_word_shield(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    opp_idx = 1-my_idx
    match target:
        case EnemyMinion(mn_idx):
            mn=state.players[opp_idx].board[mn_idx]
        case FriendlyMinion(mn_idx):
            mn=state.players[my_idx].board[mn_idx]
        case _:
            raise InvalidTargetError()
    undo.append((UndoOp.SET_MINION_MAX_HEALTH,mn,mn.max_health))
    undo.append((UndoOp.SET_MINION_HEALTH,mn,mn.health))
    mn.max_health+=2
    mn.health+=2
    draw_card(state,my_idx,undo)
    

def _reach_equilibrium(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("reach_equilibrium effect not implemented yet")

def _wings_of_eternity(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("wings_of_eternity effect not implemented yet")

def _purifying_breath(state:GameState, my_idx:int, target:EnemyMinion|FriendlyMinion, undo:list[Move]):
    me=state.players[my_idx]
    killed = deal_damage(state,my_idx,target,me.spell_amp(5),undo)
    if killed:
        heal(state,my_idx,EnemyHero(),me.heal_power(5),undo)
    
    
    

def _ritual_of_life(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("ritual_of_life effect not implemented yet")

def _smoldering_ascent(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("smoldering_ascent effect not implemented yet")

def _twilight_influence(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("twilight_influence effect not implemented yet")
def _constricting_thorns(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("twilight_influence effect not implemented yet")
def _controlling_vines(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("twilight_influence effect not implemented yet")

def _cease_to_exist(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("cease_to_exist effect not implemented yet")

def _devouring_plague(state:GameState, my_idx:int, undo:list[Move]):
    me = state.players[my_idx]
    opp_idx = 1-my_idx
    opp = state.players[opp_idx]
    
    #shoot spell_amp(4) missiles
    for missile in me.spell_amp(4):
        if len(opp.board)<1:
            break
        mn_idx = random.choice(range(len(opp.board)))
        deal_damage(state,my_idx,EnemyMinion(mn_idx),1,undo)#need to implement no heal if it hits a divine shield
        heal(state,my_idx,FriendlyHero(),me.heal_power(1),undo)


def _eternal_firebolt(state:GameState, my_idx:int, target:FriendlyMinion|EnemyMinion, undo:list[Move]):
    opp_idx=1-my_idx
    opp=state.players[opp_idx]
    me=state.players[my_idx]

    killed = deal_damage(state,my_idx,target,me.spell_amp(3),undo)
    if killed:
        heal(state,my_idx,FriendlyHero(),me.heal_power(me.spell_amp(3)))

            
def _holy_nova(state:GameState, my_idx:int, undo:list[Move]):
    me = state.players[my_idx]
    opp_idx = 1-my_idx
    opp = state.players[opp_idx]
    
    #spell effect
    for mn in opp.board:
        undo.append((UndoOp.SET_MINION_HEALTH,mn,mn.health))
        mn.health-=me.spell_amp(2)
    for mn in me.board:
        undo.append((UndoOp.SET_MINION_HEALTH,mn,mn.health))
        mn.health+=me.heal_power(2)
    me.hp=min(me.hp+me.heal_power(2),me.max_hp)
    #aftermath, important to apply spell effect before deathrattles
    for mn_idx in range(len(opp.board)):
        mn=opp.board[mn_idx]
        if mn.health<1:
            kill_minion(state,opp_idx,mn_idx,undo)
    for mn_idx in range(len(me.board)):#if healing deals dmg need to check friendlies
        mn=me.board[mn_idx]
        if mn.health<1:
            kill_minion(state,my_idx,mn_idx,undo)

    
def _intertwined_fate(state:GameState, my_idx:int, undo:list[Move]):
    raise NotImplementedError("intertwined_fate effect not implemented yet")

def _light_of_the_new_moon(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("light_of_the_new_moon effect not implemented yet")

def _wish_of_the_new_moon(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("wish_of_the_new_moon effect not implemented yet")

def _for_all_time(state:GameState, my_idx:int, undo:list[Move]):
    for owner_idx in 0,2,1:#dont care about setting hp to 0 just clear all minions <=4attack
        for mn_idx in range(len(state.players[owner_idx].board)):
            if state.players[owner_idx].board[mn_idx].attack<5:
                kill_minion(state,owner_idx,mn_idx,undo)
    undo.append((UndoOp.SET_OVERLOAD,my_idx,state.players[my_idx].overload))
    state.players[my_idx].overload+=2
    

def _gravedawn_sunbloom(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("gravedawn_sunbloom effect not implemented yet")

def _gravedawn_voidbulb(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("gravedawn_voidbulb effect not implemented yet")

def _greater_healing_potion(state:GameState, my_idx:int, target:FriendlyHero|FriendlyMinion, undo:list[Move]):
    me = state.players[my_idx]
    heal(state,my_idx,target,me.heal_power(12),undo)
    draw_card(state,my_idx,undo)

def _schism(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("schism effect not implemented yet")

def _shadow_word_ruin(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    for owner_idx in 0,2,1:#dont care about setting hp to 0 just clear all minions >=5 attack
        for mn_idx in range(len(state.players[owner_idx].board)):
            if state.players[owner_idx].board[mn_idx].attack>4:
                kill_minion(state,owner_idx,mn_idx,undo)

def _void_shard(state:GameState, my_idx:int, target:Target, undo:list[Move]):#need divine shield case here too
    opp_idx = 1-my_idx
    me,opp = state.players[my_idx],state.players[opp_idx]
    deal_damage(state,my_idx,target,me.spell_amp(4),undo)
    heal(state,my_idx,FriendlyHero(),me.heal_power(me.spell_amp(4)))
        
        


def _medivhs_triumph(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("medivhs_triumph effect not implemented yet")

def _ritual_of_the_new_moon(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("ritual_of_the_new_moon effect not implemented yet")

def _initiation(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("initiation effect not implemented yet")

def _moonwell(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("moonwell effect not implemented yet")

def _resuscitate(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("resuscitate effect not implemented yet")

def _behemoth_mask(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("behemoth_mask effect not implemented yet")

def _story_of_amara(state:GameState, my_idx:int, target:Target, undo:list[Move]):
    raise NotImplementedError("story_of_amara effect not implemented yet")



class InvalidTargetError(Exception):
    pass