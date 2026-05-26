from enum import IntEnum
from game.state import GameState, PlayerState, Minion
from game.cards import CardName

class Op(IntEnum):
    #game stats
    SET_CURRENT_PLAYER=0
    SET_TURN_NUMBER=1
    SET_WINNER=2

    #player stats
    SET_PLAYER_HP=50
    SET_PLAYER_MANA=51
    SET_PLAYER_MAX_MANA=52
    BOARD_INSERT=53
    BOARD_DEL=54
    INSERT_PLAYER_DECK=55
    DEL_PLAYER_DECK=56
    INSERT_PLAYER_HAND=57
    DEL_PLAYER_HAND=58
    SPAWN_CARD=59
    SET_HERO_POWER_USED=60
    SET_HERO_POWER_POWER=61
    SET_FATIGUE_COUNTER=62
    SET_ALEXSTRASZA_GUARDIAN_OF_LIFE_CHARGES=63
    
    

    #minion stats
    SET_MINION_ATTACK=100
    SET_MINION_HEALTH=101
    SET_MINION_MAX_HEALTH=102
    SET_MINION_TAUNT=103
    SET_MINION_CAN_ATTACK=104


def undo_one(state:GameState, op):

    match op:
        #GAME OPS
        case(Op.SET_CURRENT_PLAYER, player_idx):
            state.current_player=player_idx

        case(Op.SET_TURN_NUMBER,turn_number):
            state.turn_number=turn_number

        case(Op.SET_WINNER,winner_idx):
            state.winner=winner_idx


        #PLAYER OPS
        case (Op.SET_PLAYER_HP,player_idx,old_hp):
            me:PlayerState = state.players[player_idx]
            me.hp = old_hp

        case (Op.SET_PLAYER_MANA,player_idx,old_mana):
            me:PlayerState = state.players[player_idx]
            me.mana = old_mana

        case(Op.SET_PLAYER_MAX_MANA,player_idx,old_max_mana):
            me:PlayerState = state.players[player_idx]
            me.max_mana=old_max_mana

        case(Op.BOARD_INSERT,player_idx,board_idx,minion):
            me:PlayerState = state.players[player_idx]
            me.board.insert(board_idx, minion)

        case(Op.BOARD_DEL,player_idx,board_idx):
            me:PlayerState = state.players[player_idx]
            me.board.pop(board_idx)

        case(Op.INSERT_PLAYER_DECK,player_idx,deck_idx,card_name):
            me:PlayerState = state.players[player_idx]
            me.deck.insert(deck_idx,card_name)

        case(Op.DEL_PLAYER_DECK,player_idx,deck_idx):
            me:PlayerState = state.players[player_idx]
            me.deck.pop(deck_idx)

        case(Op.INSERT_PLAYER_HAND,player_idx,hand_idx,card):
            me:PlayerState = state.players[player_idx]
            me.hand.insert(hand_idx,card)

        case(Op.DEL_PLAYER_HAND,player_idx,hand_idx):
            me:PlayerState = state.players[player_idx]
            me.hand.pop(hand_idx)

        case(Op.SPAWN_CARD,player_idx,hand_idx,card):
            me:PlayerState = state.players[player_idx]
            me.hand.insert(hand_idx,card)

        case(Op.SET_HERO_POWER_USED,player_idx,status):
            me:PlayerState = state.players[player_idx]
            me.hero_power_used = status

        case(Op.SET_HERO_POWER_POWER,player_idx,power):
            me:PlayerState = state.players[player_idx]
            me.hero_power_power = power

        case(Op.SET_FATIGUE_COUNTER,player_idx,fatigue_counter):
            me:PlayerState = state.players[player_idx]
            me.fatigue_counter=fatigue_counter

        case(Op.SET_ALEXSTRASZA_GUARDIAN_OF_LIFE_CHARGES,player_idx,charges):
            me:PlayerState = state.players[player_idx]
            me.alexstrasza_guardian_of_life_charges = charges


        #MINION OPS
        case(Op.SET_MINION_ATTACK,mn,old_attack):
            mn:Minion = mn
            mn.attack = old_attack

        case(Op.SET_MINION_HEALTH,mn,old_health):
            mn:Minion=mn
            mn.health=old_health

        case(Op.SET_MINION_MAX_HEALTH,mn,old_max_health):
            mn:Minion = mn
            mn.max_health = old_max_health

        case(Op.SET_MINION_TAUNT,mn,old_taut_status):
            mn:Minion = mn
            mn.taunt = old_taut_status

        case(Op.SET_MINION_CAN_ATTACK,mn,old_can_attack):
            mn:Minion = mn
            mn.can_attack = old_can_attack
        
            
def undo_move(state, undo_record):
    for op in reversed(undo_record):
        undo_one(state,op)


