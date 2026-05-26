from game import moves as m
from game import state as s
from game import cards as c
import copy
import random
from game import effects


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
            card_def = c.CARD_DEFS[card_name]
            if card_def.cost <= player.mana:
                # For v1, only one board position matters (rightmost)
                out.append(m.PlayMinion(hand_index=idx, board_position=len(player.board)))


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


def apply_move(state: s.GameState, move: m.Move) -> s.GameState:
    """Apply a move and return a NEW GameState. Original is not mutated."""

    def _heal(current:s.PlayerState,target, heal):
        match target:
                case m.FriendlyHero():
                    current.hp = min(current.hp + heal, current.max_hp)
                    if current.hp==current.max_hp and current.alexstraza_guardian_of_life_charges>0:
                        for _ in range(current.alexstraza_guardian_of_life_charges):
                            new_state.players[1-state.current_player].hp-=15
                        current.alexstraza_guardian_of_life_charges=0
                case m.EnemyHero():
                    other.hp = min(other.hp + heal, other.max_hp)
                case m.FriendlyMinion(index=i):
                    mn = current.board[i]
                    mn.health = min(mn.health + heal, mn.max_health)
                case m.EnemyMinion(index=i):
                    mn = other.board[i]
                    mn.health = min(mn.health + heal, mn.max_health)
        return


    new_state = copy.deepcopy(state)
    current = new_state.players[new_state.current_player]
    other = new_state.players[1 - new_state.current_player]

    match move:
        case m.PlayMinion(hand_index=i, board_position=pos):
            card_name = current.hand.pop(i)
            card_def = c.CARD_DEFS[card_name]
            current.mana -= card_def.cost
            if card_name in effects.INSTANT_BATTLECRIES:
                effects.INSTANT_BATTLECRIES[card_name](new_state, new_state.current_player)
            new_minion = s.Minion(
                card=card_name,
                attack=card_def.attack,
                health=card_def.health,
                max_health=card_def.health,
                taunt=card_def.taunt,
                can_attack=False,
            )
            current.board.insert(pos, new_minion)

        case m.Attack(attacker_index=ai, target_index=ti):
            attacker = current.board[ai]
            defender = other.board[ti]
            defender.health -= attacker.attack
            attacker.health -= defender.attack
            attacker.can_attack = False
            current.board = [mn for mn in current.board if mn.health > 0]
            other.board = [mn for mn in other.board if mn.health > 0]

        case m.AttackHero(attacker_index=ai):
            attacker = current.board[ai]
            other.hp -= attacker.attack
            attacker.can_attack = False

        case m.HeroPower(target=target):
            current.mana -= 2
            current.hero_power_used = True
            heal = current.hero_power_power
            _heal(current, target, heal)
            
        case m.EndTurn():
            new_state.current_player = 1 - new_state.current_player
            new_state.turn_number += 1
            _start_turn(new_state)

    _check_winner(new_state)
    return new_state
    




def _start_turn(state: s.GameState) -> None:
    player = state.players[state.current_player]
    player.max_mana = min(player.max_mana + 1, 10)
    player.mana = player.max_mana
    player.hero_power_used = False
    for mn in list(player.board):#dont want to mutate what im iterating over
        mn.can_attack = True
        if mn.card in effects.START_OF_TURN:
            effects.START_OF_TURN[mn.card](state, state.current_player)
    _draw_card(state, state.current_player)


def _draw_card(state: s.GameState, player_index: int) -> None:
    player = state.players[player_index]
    if player.deck:
        card = player.deck.pop(0)
        if len(player.hand) < 10:
            player.hand.append(card)
        # else: card is burned (discarded)
    else:
        player.fatigue_counter += 1
        player.hp -= player.fatigue_counter


def _check_winner(state: s.GameState) -> None:
    p0_dead = state.players[0].hp <= 0
    p1_dead = state.players[1].hp <= 0
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
        deck=c.STARTER_DECK

    p0_deck = list(deck)
    p1_deck = list(deck)
    random.shuffle(p0_deck)
    random.shuffle(p1_deck)

    p0 = s.PlayerState(deck=p0_deck)
    p1 = s.PlayerState(deck=p1_deck)

    state = s.GameState(players=(p0,p1), current_player=0)
    
    for _ in range(3):
        _draw_card(state, 0)
    for _ in range(4):
        _draw_card(state, 1)

    p0.max_mana=1
    p0.mana=1
    p1.max_mana=0

    return state

