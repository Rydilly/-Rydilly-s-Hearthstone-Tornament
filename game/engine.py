from game import moves as m
from game import state as s
from game import cards as c
from game import spells 
import copy
import random
from game import effects
from game.undo import Op as UndoOp
from game.helpers import kill_minion, draw_card


def legal_moves(state: s.GameState) -> list[m.Move]:
    """Return all legal moves for the current player."""
    if state.winner is not None:
        return []

    out: list[m.Move] = [m.EndTurn()]
    player = state.players[state.current_player]
    opponent = state.players[1 - state.current_player]

    # Attacks
    enemy_taunts = [i for i, mn in enumerate(opponent.board) if mn.taunt]

    for ai, attacker in enumerate(player.board):
        if not attacker.can_attack or attacker.attack <= 0:
            continue
        if enemy_taunts:
            for ti in enemy_taunts:
                out.append(m.Attack(attacker_index=ai, target_index=ti))
        else:
            for ti in range(len(opponent.board)):
                out.append(m.Attack(attacker_index=ai, target_index=ti))
            out.append(m.AttackHero(attacker_index=ai))

    # Play minions from hand
    if len(player.board) < 7:
        for idx, card_name in enumerate(player.hand):
            if isinstance(c.CARD_DEFS[player.hand[idx]], c.MinionDef):
                card_def = c.CARD_DEFS[card_name]
                if card_def.cost <= player.mana:
                    # For v1, only one board position matters (rightmost)
                    out.append(m.PlayMinion(hand_index=idx, board_position=len(player.board)))


    #Play spells form hand

    for idx in range(len(player.hand)):
        if isinstance(c.CARD_DEFS[player.hand[idx]],c.SpellDef):#if the card is a spell
            spell:c.SpellDef = c.CARD_DEFS[player.hand[idx]]
            if spell.cost>player.mana:
                pass
            if spell.target is None:
                out.append(m.PlaySpell(hand_index=idx,target=None))
                break
            if m.EnemyMinion in spell.target:
                for mn_idx in range(len(opponent.board)):
                    out.append(m.PlaySpell(hand_index=idx,target=m.EnemyMinion(mn_idx)))
            if m.FriendlyMinion in spell.target:
                for mn_idx in range(len(player.board)):
                    out.append(m.PlaySpell(hand_index=idx,target=m.FriendlyMinion(mn_idx)))
            if m.EnemyHero in spell.target:
                out.append(m.PlaySpell(hand_index=idx,target=m.EnemyHero()))
            if m.FriendlyHero in spell.target:
                out.append(m.PlaySpell(hand_index=idx,target=m.FriendlyHero()))



    # Hero power
    if not player.hero_power_used and player.mana >= 2:
        if player.hp < player.max_hp:
            out.append(m.HeroPower(target=m.FriendlyHero()))
        if opponent.hp < opponent.max_hp:
            out.append(m.HeroPower(target=m.EnemyHero()))
        for i, mn in enumerate(player.board):
            if mn.health < mn.max_health:
                out.append(m.HeroPower(target=m.FriendlyMinion(index=i)))
        for i, mn in enumerate(opponent.board):
            if mn.health < mn.max_health:
                out.append(m.HeroPower(target=m.EnemyMinion(index=i)))

    return out


HEAL_AMOUNT = 2

def apply_move(state: s.GameState, move: m.Move) -> list:
    """Apply a move and mutate an undo:list. Original is mutated. undo list is returned"""
    undo=[]
    me_idx = state.current_player
    opp_idx = 1-state.current_player
    me = state.players[me_idx]
    opp = state.players[opp_idx]
    
    match move:
        case m.EndTurn():
            #flipping current player


            undo.append((UndoOp.SET_CURRENT_PLAYER,me_idx))
            state.current_player = 1-me_idx

            #incrementing turn number
            undo.append((UndoOp.SET_TURN_NUMBER,state.turn_number))
            state.turn_number+=1
            _start_turn(state,undo)

        case m.PlaySpell(hand_idx,target):
            #removing card from hand
            card_name = me.hand.pop(hand_idx)
            undo.append((UndoOp.INSERT_PLAYER_HAND,me_idx,hand_idx,card_name))

            #card lookup
            card_stats = c.CARD_DEFS[card_name]

            #subtracting mana
            undo.append((UndoOp.SET_PLAYER_MANA,me_idx,me.mana))
            me.mana-=card_stats.cost

            #let spell do its thing
            print(f"Playing Spell:{card_name}")
            spells.PRIEST_SPELLS[card_name](state,me_idx,target,undo)
    

        case m.PlayMinion(hand_idx,board_idx):
            #removing the card from hand
            card_name = me.hand.pop(hand_idx)
            undo.append((UndoOp.INSERT_PLAYER_HAND,me_idx,hand_idx,card_name))

            #card lookup
            card_stats = c.CARD_DEFS[card_name]

            #subtracting mana
            undo.append((UndoOp.SET_PLAYER_MANA,me_idx,me.mana))
            me.mana-=card_stats.cost

            #checking and running battle cry
            if card_name in effects.INSTANT_BATTLECRIES:
                effects.INSTANT_BATTLECRIES[card_name](state,me_idx,undo)#its the battlecry responsibility to update undo

            #building a minion. py garbage collector will clean up on undo
            new_minion = s.Minion(
                card=card_name,
                attack=card_stats.attack,
                health=card_stats.health,
                max_health=card_stats.health,
                taunt=card_stats.taunt,
                can_attack=False
            )
            
            #insert minion onto board
            undo.append((UndoOp.BOARD_DEL,me_idx,board_idx))
            me.board.insert(board_idx,new_minion)
   

        case m.Attack(atta_idx, targ_idx):
            attacker:s.Minion = me.board[atta_idx]
            target:s.Minion = opp.board[targ_idx]
            
            #set new minion health
            undo.append((UndoOp.SET_MINION_HEALTH,attacker,attacker.health))
            undo.append((UndoOp.SET_MINION_HEALTH,target,target.health))
            attacker.health-=target.attack
            target.health-=attacker.attack

            #Remove killed from board or update can_attack status
            if attacker.health<1:
                kill_minion(state,me_idx,atta_idx,undo)
            else:
                undo.append((UndoOp.SET_MINION_CAN_ATTACK,attacker,True))
                attacker.can_attack=False
            if target.health<1:
                kill_minion(state,opp_idx,targ_idx,undo)


        case m.AttackHero(atta_idx):
            attacker=me.board[atta_idx]

            #reducing hp
            undo.append((UndoOp.SET_PLAYER_HP,opp_idx,opp.hp))
            opp.hp-=attacker.attack

            #update attack status
            undo.append((UndoOp.SET_MINION_CAN_ATTACK,attacker,True))
            attacker.can_attack=False
            
        case m.HeroPower(target):
            
            #update mana
            undo.append((UndoOp.SET_PLAYER_MANA,me_idx,me.mana))
            me.mana-=2

            #update hero power used
            undo.append((UndoOp.SET_HERO_POWER_USED,me_idx,False))
            me.hero_power_used=True

            match target:
                case m.FriendlyHero():
                    undo.append((UndoOp.SET_PLAYER_HP,me_idx,me.hp))
                    me.hp = min(me.max_hp,me.hp+me.hero_power_power)
                    #if hero has alexstraza charges
                    if me.hp==me.max_hp and me.alexstrasza_guardian_of_life_charges>0:
                        for _ in range(me.alexstrasza_guardian_of_life_charges):
                            undo.append((UndoOp.SET_PLAYER_HP,opp_idx,opp.hp))
                            opp.hp-=15
                        undo.append((UndoOp.SET_ALEXSTRASZA_GUARDIAN_OF_LIFE_CHARGES,me_idx,me.alexstrasza_guardian_of_life_charges))
                        me.alexstrasza_guardian_of_life_charges=0
                
                case m.EnemyHero():
                    undo.append((UndoOp.SET_PLAYER_HP,opp_idx,opp.hp))
                    opp.hp = min(opp.hp+opp.hero_power_power, opp.max_hp)
                
                case m.FriendlyMinion(i):
                    mn:s.Minion = me.board[i]
                    
                    undo.append((UndoOp.SET_MINION_HEALTH,mn,mn.health))
                    mn.health= min(mn.health+me.hero_power_power,mn.max_health)

                case m.EnemyMinion(i):
                    mn:s.Minion = opp.board[i]

                    undo.append((UndoOp.SET_MINION_HEALTH,mn,mn.health))
                    mn.health= min(mn.health+me.hero_power_power,mn.max_health)



            
        
    _check_winner(state, undo)
    return undo
    




def _start_turn(state: s.GameState, undo:list) -> None:
    """mutates state and undo list returning nothing"""
    player = state.players[state.current_player]

    #incrementing max mana
    if player.max_mana<10:
        undo.append((UndoOp.SET_PLAYER_MAX_MANA,state.current_player,player.max_mana))
        player.max_mana = player.max_mana + 1

    #filling mana pool
    undo.append((UndoOp.SET_PLAYER_MANA,state.current_player,player.mana))
    player.mana = player.max_mana-player.overload
    player.overload=0

    #hero power used reset
    if player.hero_power_used:
        undo.append((UndoOp.SET_HERO_POWER_USED,state.current_player,True))
        player.hero_power_used = False

    #minion start of turn effects
    for mn in list(player.board):#dont want to mutate what im iterating over
        if not mn.can_attack and mn.attack>0:
            undo.append((UndoOp.SET_MINION_CAN_ATTACK,mn,False))
            mn.can_attack = True
        if mn.card in effects.START_OF_TURN:
            #it is each effects job to log what it does onto undo
            effects.START_OF_TURN[mn.card](state, state.current_player, undo)

        

    draw_card(state, state.current_player,undo)




def _check_winner(state: s.GameState, undo:list) -> None:
    p0_dead = state.players[0].hp <= 0
    p1_dead = state.players[1].hp <= 0
    if not p0_dead and not p1_dead:
        return
    undo.append((UndoOp.SET_WINNER,state.winner))
    if p0_dead and p1_dead:
        state.winner = -1  # tie
    elif p0_dead:
        state.winner = 1
    elif p1_dead:
        state.winner = 0


def new_game(deck: list[c.CardName]|None = None, seed:int|None=None)->s.GameState:
    if seed is not None:
        random.seed(seed)
    
    if deck is None:
        deck=c.Spell_test

    p0_deck = list(deck)
    p1_deck = list(deck)
    random.shuffle(p0_deck)
    random.shuffle(p1_deck)

    p0 = s.PlayerState(deck=p0_deck)
    p1 = s.PlayerState(deck=p1_deck)

    state = s.GameState(players=(p0,p1), current_player=0)
    
    for _ in range(3):
        draw_card(state, 0, [])
    for _ in range(4):
        draw_card(state, 1, [])

    p0.max_mana=1
    p0.mana=1
    p1.max_mana=0

    return state

if __name__=="__main__":
    from game.moves import EndTurn,PlayMinion,HeroPower,FriendlyHero
    from game.undo import undo_move
    from dataclasses import asdict
    from game.cards import CardName

    state = new_game()
    state.players[0].max_mana=10
    state.players[1].max_mana=10
    cp = copy.deepcopy(state)
    undo = []
    
    #print(state.players[state.current_player].hand)

    undo.append(apply_move(state,EndTurn()))
    undo.append(apply_move(state,EndTurn()))
    undo.append(apply_move(state,PlayMinion(0,0)))
    #play alexstrasza

    state.players[state.current_player].hand.append(CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE)
    state.players[1-state.current_player].hand.append(CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE)
    cp.players[state.current_player].hand.append(CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE)
    cp.players[1-state.current_player].hand.append(CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE)
    undo.append(apply_move(state,PlayMinion(len(state.players[state.current_player].hand)-1,1)))
    


    while state.players[state.current_player].hp<state.players[state.current_player].max_hp:
        undo.append(apply_move(state,HeroPower(FriendlyHero())))
    assert state.players[1-state.current_player].hp == state.players[1-state.current_player].max_hp-15,f"opp current hp: {state.players[1-state.current_player].hp}\nmy current hp:{state.players[state.current_player].hp}\nMy Board:{state.players[state.current_player].board}"

    while len(undo)>0:
        undo_move(state,undo.pop())


    assert asdict(cp) == asdict(state)
    #asdict is slow but easy way to compare 2 instances



