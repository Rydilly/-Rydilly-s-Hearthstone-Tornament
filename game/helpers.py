from game.state import PlayerState, GameState
from undo import Op as UndoOp
from moves import Target,Move,EnemyHero,EnemyMinion,FriendlyHero,FriendlyMinion



def kill_minion(state:GameState, player_idx, board_idx, undo:list):
    mn = state.players[player_idx].board[board_idx]
    undo.append((UndoOp.BOARD_INSERT,player_idx,board_idx,mn))
    #insert deathrattle effect here when rdy
    state.players[player_idx].board.pop(board_idx)


def draw_card(state: GameState, player_idx: int, undo:list) -> None:
    """draws a card mutating gamestate and undo. returns nothing"""
    player = state.players[player_idx]
    if player.deck:
        card = player.deck.pop()
        undo.append((UndoOp.INSERT_PLAYER_DECK,player_idx,len(player.deck),card))
        if len(player.hand) < 10:
            undo.append((UndoOp.DEL_PLAYER_HAND,player_idx,len(player.hand)))
            player.hand.append(card)
        # else: card is burned (discarded)
    else:
        undo.append((UndoOp.SET_FATIGUE_COUNTER,player_idx,player.fatigue_counter))
        player.fatigue_counter += 1
        undo.append((UndoOp.SET_PLAYER_HP,player_idx,player.hp))
        player.hp -= player.fatigue_counter

def deal_damage(state:GameState, my_idx:int, target:Target, dmg:int, undo:list)->bool:
    """
    does not apply amp. returns true if it kills a minion
    """
    opp_idx = 1-my_idx
    me,opp = state.players[my_idx],state.players[my_idx]
    
    match target:
        case EnemyHero():
            undo.append((UndoOp.SET_PLAYER_HP,opp_idx,opp.hp))
            opp.hp-=dmg
        case EnemyMinion(mn_idx):
            mn=opp.board[mn_idx]
            undo.append((UndoOp.SET_MINION_HEALTH,state,mn,mn.health))
            mn_idx-=dmg
            if mn.health<1:
                kill_minion(state,opp_idx,mn_idx,undo)
                return True
        case FriendlyHero():
            undo.append((UndoOp.SET_PLAYER_HP,my_idx,me.hp))
            opp.hp-=dmg
        case FriendlyMinion(mn_idx):
            mn=me.board[mn_idx]
            undo.append((UndoOp.SET_MINION_HEALTH,state,mn,mn.health))
            mn_idx-=dmg
            if mn.health<1:
                kill_minion(state,my_idx,mn_idx,undo)
                return True
    return False

def heal(state:GameState, my_idx:int, target:Target, heal:int, undo:list):
    """
    amp not applied
    """
    opp_idx = 1-my_idx
    me,opp = state.players[my_idx],state.players[my_idx]
    
    match target:
        case EnemyHero():
            undo.append((UndoOp.SET_PLAYER_HP,opp_idx,opp.hp))
            opp.hp=min(opp.max_hp,opp.hp+heal)
        case EnemyMinion(mn_idx):
            mn=opp.board[mn_idx]
            undo.append((UndoOp.SET_MINION_HEALTH,state,mn,mn.health))
            mn_idx=min(mn.max_health,mn.health+heal)
            if mn.health<1:
                kill_minion(state,opp_idx,mn_idx,undo)
        case FriendlyHero():
            undo.append((UndoOp.SET_PLAYER_HP,my_idx,me.hp))
            opp.hp=min(opp.max_hp,opp.hp+heal)
        case FriendlyMinion(mn_idx):
            mn=me.board[mn_idx]
            undo.append((UndoOp.SET_MINION_HEALTH,state,mn,mn.health))
            mn_idx=min(mn.max_health,mn.health+heal)
            if mn.health<1:
                kill_minion(state,my_idx,mn_idx,undo)
