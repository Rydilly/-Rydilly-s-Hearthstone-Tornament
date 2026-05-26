"""
Quick smoke tests for the game engine.
Run with: python play.py
"""

from game import cards as c
from game import engine as e
from game import moves as m
from game import state as s
from bots import lethal_bot as l
from bots import value_bot as v
from bots.doomsayer_smart_bot import Doomsayer_smart_bot as doom 
from game.cards import CardName
from play import play_game




def make_empty_state(
    p0_hand=None,
    p0_deck=None,
    p0_board=None,
    p0_mana=10,
    p0_hp=20,
    p1_hand=None,
    p1_deck=None,
    p1_board=None,
    p1_mana=10,
    p1_hp=20,
    current_player=0,
):
    """Helper: build a GameState with whatever you want to test."""
    p0 = s.PlayerState(
        hp=p0_hp,
        max_hp=20,
        mana=p0_mana,
        max_mana=p0_mana,
        hand=p0_hand or [],
        deck=p0_deck or [],
        board=p0_board or [],
    )
    p1 = s.PlayerState(
        hp=p1_hp,
        max_hp=20,
        mana=p1_mana,
        max_mana=p1_mana,
        hand=p1_hand or [],
        deck=p1_deck or [],
        board=p1_board or [],
    )
    return s.GameState(players=(p0, p1), current_player=current_player)


def make_minion(attack, health, taunt=False, can_attack=True, card=None):
    """Helper: build a Minion directly on a board, bypassing PlayMinion."""
    card_name = card or c.CardName.ACOLYTE_OF_PAIN  # arbitrary default
    return s.Minion(
        card=card_name,
        attack=attack,
        health=health,
        max_health=health,
        taunt=taunt,
        can_attack=can_attack,
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_play_minion_costs_mana():
    card_name = c.CardName.ACOLYTE_OF_PAIN
    cost = c.CARD_DEFS[card_name].cost
    state = make_empty_state(p0_hand=[card_name], p0_mana=10)

    new_state = e.apply_move(state, m.PlayMinion(hand_index=0, board_position=0))

    assert new_state.players[0].mana == 10 - cost, (
        f"Expected mana {10 - cost}, got {new_state.players[0].mana}"
    )
    assert len(new_state.players[0].hand) == 0, "Card should leave hand"
    assert len(new_state.players[0].board) == 1, "Minion should be on board"
    print("✓ test_play_minion_costs_mana")


def test_played_minion_has_summoning_sickness():
    card_name = c.CardName.ACOLYTE_OF_PAIN
    state = make_empty_state(p0_hand=[card_name], p0_mana=10)

    new_state = e.apply_move(state, m.PlayMinion(hand_index=0, board_position=0))

    assert new_state.players[0].board[0].can_attack is False, (
        "Newly played minion should not be able to attack"
    )
    print("✓ test_played_minion_has_summoning_sickness")


def test_attack_kills_both_when_equal():
    # 3/3 attacks 3/3 → both die
    attacker = make_minion(3, 3)
    defender = make_minion(3, 3)
    state = make_empty_state(p0_board=[attacker], p1_board=[defender])

    new_state = e.apply_move(
        state, m.Attack(attacker_index=0, target_index=0)
    )

    assert len(new_state.players[0].board) == 0, "Attacker should be dead"
    assert len(new_state.players[1].board) == 0, "Defender should be dead"
    print("✓ test_attack_kills_both_when_equal")


def test_attack_only_kills_weaker():
    # 5/5 attacks 3/3 → defender dies, attacker survives at 2 HP
    attacker = make_minion(5, 5)
    defender = make_minion(3, 3)
    state = make_empty_state(p0_board=[attacker], p1_board=[defender])

    new_state = e.apply_move(
        state, m.Attack(attacker_index=0, target_index=0)
    )

    assert len(new_state.players[0].board) == 1, "Attacker should survive"
    assert new_state.players[0].board[0].health == 2, "Attacker should be at 2 HP"
    assert len(new_state.players[1].board) == 0, "Defender should be dead"
    print("✓ test_attack_only_kills_weaker")


def test_attack_hero_reduces_hp():
    attacker = make_minion(4, 4)
    state = make_empty_state(p0_board=[attacker], p1_hp=20)

    new_state = e.apply_move(state, m.AttackHero(attacker_index=0))

    assert new_state.players[1].hp == 16, (
        f"Expected enemy hero at 16 HP, got {new_state.players[1].hp}"
    )
    print("✓ test_attack_hero_reduces_hp")


def test_attack_hero_lethal_sets_winner():
    attacker = make_minion(20, 20)
    state = make_empty_state(p0_board=[attacker], p1_hp=5)

    new_state = e.apply_move(state, m.AttackHero(attacker_index=0))

    assert new_state.winner == 0, (
        f"Expected player 0 to win, got winner={new_state.winner}"
    )
    print("✓ test_attack_hero_lethal_sets_winner")


def test_hero_power_heals_friendly_hero():
    state = make_empty_state(p0_hp=10, p0_mana=10)

    new_state = e.apply_move(state, m.HeroPower(target=m.FriendlyHero()))

    assert new_state.players[0].hp == 12, (
        f"Expected hero at 12 HP, got {new_state.players[0].hp}"
    )
    assert new_state.players[0].mana == 8, "Hero power should cost 2 mana"
    assert new_state.players[0].hero_power_used is True
    print("✓ test_hero_power_heals_friendly_hero")


def test_hero_power_caps_at_max_hp():
    state = make_empty_state(p0_hp=19, p0_mana=10)

    new_state = e.apply_move(state, m.HeroPower(target=m.FriendlyHero()))

    assert new_state.players[0].hp == 20, "Heal should cap at max_hp"
    print("✓ test_hero_power_caps_at_max_hp")


def test_end_turn_switches_player():
    state = make_empty_state(current_player=0)

    new_state = e.apply_move(state, m.EndTurn())

    assert new_state.current_player == 1, "Turn should switch to player 1"
    print("✓ test_end_turn_switches_player")


def test_end_turn_clears_summoning_sickness():
    sick_minion = make_minion(3, 3, can_attack=False)
    state = make_empty_state(p1_board=[sick_minion], current_player=0)

    # After end turn, it becomes player 1's turn — their minion should be ready
    new_state = e.apply_move(state, m.EndTurn())

    assert new_state.players[1].board[0].can_attack is True, (
        "Minion should be able to attack on its owner's next turn"
    )
    print("✓ test_end_turn_clears_summoning_sickness")


def test_apply_move_does_not_mutate_input():
    """Critical for MCTS: the original state must be unchanged."""
    card_name = c.CardName.ACOLYTE_OF_PAIN
    state = make_empty_state(p0_hand=[card_name], p0_mana=10)
    original_hand_len = len(state.players[0].hand)
    original_mana = state.players[0].mana

    e.apply_move(state, m.PlayMinion(hand_index=0, board_position=0))

    assert len(state.players[0].hand) == original_hand_len, (
        "Original state's hand should not change!"
    )
    assert state.players[0].mana == original_mana, (
        "Original state's mana should not change!"
    )
    print("✓ test_apply_move_does_not_mutate_input")



def test_found_lethal():
    state = make_empty_state(p0_board=[make_minion(5,5,can_attack=True)], p1_hp=5, current_player=0)
    
    bot = l.Lethal_Bot(use_persistent_cache=False)
    print("making move in test_found_lethal")
    move = bot.pick_move(state)
    print(f"got move {move}")
    new_state = e.apply_move(state, move)
    assert new_state.winner == 0
    print("Lethal_Bot is finding lethal")


def test_fallback_matches_valuebot():
    state = make_empty_state(
        p0_board=[make_minion(3, 3, can_attack=True), make_minion(2, 2, can_attack=True)],
        p1_hp=20,  # too much HP for lethal
        p0_mana=10,
        p1_board=[make_minion(4, 4)]
    )
    
    lethal_bot = l.Lethal_Bot(use_persistent_cache=False)
    value_bot = v.ValueBot()
    
    lethal_move = lethal_bot.pick_move(state)
    value_move = value_bot.pick_move(state)
    
    print(f"LethalBot picked: {lethal_move}")
    print(f"ValueBot picked:  {value_move}")
    
    # They should match when no lethal is possible
    assert lethal_move == value_move, f"Mismatch! Lethal={lethal_move}, Value={value_move}"


def test_doomsayer_wipes_on_start_of_turn():
    doomsayer = make_minion(0,7,card = c.CardName.DOOMSAYER,can_attack=False)
    other_minion = make_minion(3,3)
    state = make_empty_state(
        p0_board=[other_minion],
        p1_board=[doomsayer],
        current_player=0
    )
    new_state = e.apply_move(state,m.EndTurn())
    #print(f"\n{new_state.players[0].board},\n {new_state.players[1].board}\n")
    assert new_state.players[0].board==[]
    assert new_state.players[1].board==[]

def test_alexstrasza_hp_and_dmg():
    state = make_empty_state(
        p0_hand=[c.CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE],
        p0_mana=10,
        p0_hp=10,
        p1_hp=29,
        current_player=0
    )
    new_state = e.apply_move(state, m.PlayMinion(hand_index=0, board_position=0))
    assert new_state.players[0].hp==15, f"expected 15, got {new_state.players[0].hp}... opp_hp: {new_state.players[1].hp}"

    new_state.players[0].hero_power_power=100
    final_state = e.apply_move(new_state, m.HeroPower(target=m.FriendlyHero()))
    assert final_state.players[1].hp==14, f"expexed 14, got{final_state.players[1].hp}"

def test_update_on_end_turn():
    bot1 = doom()
    bot2=doom()

    play_game(bot1,bot2)
    #print(f"bot1 weight: {bot1.eyes.weights[CardName.DOOMSAYER]}")
    assert 0<bot1.eyes.weights[CardName.DOOMSAYER]<1, f"bot1 weight: {bot1.eyes.weights[CardName.DOOMSAYER]}"
    assert 0<bot2.eyes.weights[CardName.DOOMSAYER]<1
    
# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------

def run_all_tests():
    tests = [
        test_play_minion_costs_mana,
        test_played_minion_has_summoning_sickness,
        test_attack_kills_both_when_equal,
        test_attack_only_kills_weaker,
        test_attack_hero_reduces_hp,
        test_attack_hero_lethal_sets_winner,
        test_hero_power_heals_friendly_hero,
        test_hero_power_caps_at_max_hp,
        test_end_turn_switches_player,
        test_end_turn_clears_summoning_sickness,
        test_apply_move_does_not_mutate_input,
        test_found_lethal,
        test_fallback_matches_valuebot,
        test_doomsayer_wipes_on_start_of_turn,
        test_alexstrasza_hp_and_dmg,
        test_update_on_end_turn
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as ex:
            print(f"✗ {test.__name__}: {ex}")
            failed += 1
        except Exception as ex:
            print(f"✗ {test.__name__}: CRASHED — {type(ex).__name__}: {ex}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")


if __name__ == "__main__":
    run_all_tests()