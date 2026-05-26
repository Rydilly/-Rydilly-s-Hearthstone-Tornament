from game import moves as m
from game import state as s
from game import cards as c
import copy
import math 


def legal_moves(state: s.GameState)->list[m.Move]:
    out = []
    cur_player = state.players[state.currentPlayer]
    other_player = state.players[1-state.currentPlayer]
    for i in cur_player.hand:
        if c.CARD_DEFS[i].cost<=state.PlayerState.mana:
            out.append(m.PlayMinion(hand_index=i, board_position=0))#need to allow diff board pos later
    for i in cur_player.board:
        if i.canAttack:
            for j in other_player.board:
                if not (j == None):
                    out.append(m.Attack(attacker_index=i, target_index=j))
    out.append(m.EndTurn)
    no_taunt=True
    for i in other_player.board:
        if other_player.board[i].taunt==False:
            pass
        else:
            no_taunt=False
            break
    if no_taunt:
        for i in cur_player.board:
            out.append(m.AttackHero(attacker_index=i))

    if cur_player.mana>1:
        for i in cur_player.board:
            out.append(m.HeroPower(target_index=i))
        for i in other_player.board:
            out.append(m.HeroPower(target_index=i))
        m.HeroPower(EnemyHero)
        
    return out

def restructure_card_list(player_state: type[s.PlayerState]):
    """
    should be done after a card(s) has been removed from hand
    """
    for i in range(len(player_state.hand)):
        cmp_idx = i
        for j in range(i-1,-1,-1):
            if player_state.hand[j][1]>player_state.hand[cmp_idx] or None:
                player_state.hand[j],player_state.hand[cmp_idx]=player_state.hand[cmp_idx],player_state[j]
                cmp_idx-=1
            else:
                break

def restructure_board_state(player_state: type[s.PlayerState]):
    for i in range(len(player_state.board)):
        if player_state.board[i]==None:
            for j in range(i+1,len(player_state.board)):
                player_state.board[j-1]=player_state[j]
            player_state.board[len(player_state.board)]=None

                

def apply_move(state: s.GameState, move: m.Move)->s.GameState:
    new_state = copy.deepcopy(state)
    current_player_state = new_state.players[new_state.current_player]
    other_player_state = new_state.players[1-new_state.current_player]

    match move:
        case m.PlayMinion(hand_index=i, board_position=pos):
            card_name = current_player_state.hand.pop(i)
            card_def = c.CARD_DEFS[card_name]
            current_player_state.mana -= card_def.cost
            new_minion = s.Minion(
                card=card_name,
                attack=card_def.attack,
                health=card_def.health,
                max_health=card_def.health,
                taunt=card_def.taunt,
                can_attack=False,
            )
            current_player_state.board.insert(pos, new_minion)
        case m.AttackHero():
            other_player_state.hp = other_player_state.hp-current_player_state.board[move.attacker_index].attack
            current_player_state.board[move.attacker_index].can_attack=False
            if other_player_state.hp<=0:
                state.winner=state.current_player
        case m.Attack():
            minion_attacking = current_player_state.board[move.attacker_index]
            minion_defending = other_player_state.board[move.target_index]
            minion_defending.health = minion_defending.health- minion_attacking.attack
            minion_attacking.health = minion_attacking.health-minion_defending.attack
            minion_attacking.can_attack = False
            if minion_attacking.health<=0:
                current_player_state.board[move.attacker_index]=None
                current_player_state.board = [m for m in current_player_state.board if m.health > 0]
            if minion_defending.health<0:
                other_player_state.board[move.target_index]=None
                other_player_state.board = [m for m in other_player_state.board if m.health > 0]
            
        case m.HeroPower():
            current_player_state.hero_power_used=True
            targeted_minion = current_player_state.board[move.target_index]
            current_player_state.mana-=2
            current_player_state.mana-=1
            if targeted_minion.health<current_player_state.hero_power_power:
                targeted_minion.health=targeted_minion.health+current_player_state.hero_power_power
            else:
                targeted_minion.health=targeted_minion.max_health

        case m.EndTurn():
            state.current_player=1-state.current_player
            if state.current_player==0:
                state.turn_number+=1
            state.players[state.current_player].mana=state.turn_number

    return new_state

    
