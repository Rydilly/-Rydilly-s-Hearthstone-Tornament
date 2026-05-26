from game import cards as c, engine as e, moves as m, state as s
from bots import base as b, greedy_bot as g, random_bot as r


"""
Quick smoke tests for the game engine.
Run with: python play.py
"""

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
