"""
Engine tests for the v2 mutation-based API.

Pattern: apply_move(state, move) mutates state in place and returns undo.
Tests assert against `state` (not `new_state`).

Most tests also do a round-trip: snapshot state, apply, undo, assert restored.
This catches undo bugs that asserting forward-state alone would miss.
"""

from dataclasses import asdict
import copy

from game import cards as c
from game import engine as e
from game import moves as m
from game import state as s
from game.undo import undo_move, kill_minion


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def make_empty_state(
    p0_hand=None, p0_deck=None, p0_board=None, p0_mana=10, p0_hp=20,
    p1_hand=None, p1_deck=None, p1_board=None, p1_mana=10, p1_hp=20,
    current_player=0,
):
    p0 = s.PlayerState(
        hp=p0_hp, max_hp=20, mana=p0_mana, max_mana=p0_mana,
        hand=p0_hand or [], deck=p0_deck or [], board=p0_board or [],
    )
    p1 = s.PlayerState(
        hp=p1_hp, max_hp=20, mana=p1_mana, max_mana=p1_mana,
        hand=p1_hand or [], deck=p1_deck or [], board=p1_board or [],
    )
    return s.GameState(players=(p0, p1), current_player=current_player)


def make_minion(attack, health, taunt=False, can_attack=True, card=None):
    card_name = card or c.CardName.ACOLYTE_OF_PAIN
    return s.Minion(
        card=card_name, attack=attack, health=health,
        max_health=health, taunt=taunt, can_attack=can_attack,
    )


def assert_round_trip(state, move, label=""):
    """Apply move, undo, assert state restored."""
    before = asdict(state)
    undo = e.apply_move(state, move)
    e.apply_move  # just touching to avoid unused warning
    undo_move(state, undo)
    after = asdict(state)
    assert before == after, f"Round-trip failed for {label}: state not restored"


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_play_minion_costs_mana():
    card_name = c.CardName.ACOLYTE_OF_PAIN
    cost = c.CARD_DEFS[card_name].cost
    state = make_empty_state(p0_hand=[card_name], p0_mana=10)

    e.apply_move(state, m.PlayMinion(hand_index=0, board_position=0))

    assert state.players[0].mana == 10 - cost, (
        f"Expected mana {10 - cost}, got {state.players[0].mana}"
    )
    assert len(state.players[0].hand) == 0, "Card should leave hand"
    assert len(state.players[0].board) == 1, "Minion should be on board"
    print("test_play_minion_costs_mana passed")


def test_played_minion_has_summoning_sickness():
    state = make_empty_state(p0_hand=[c.CardName.ACOLYTE_OF_PAIN], p0_mana=10)

    e.apply_move(state, m.PlayMinion(hand_index=0, board_position=0))

    assert state.players[0].board[0].can_attack is False
    print("test_played_minion_has_summoning_sickness passed")


def test_attack_kills_both_when_equal():
    state = make_empty_state(
        p0_board=[make_minion(3, 3)],
        p1_board=[make_minion(3, 3)],
    )

    e.apply_move(state, m.Attack(attacker_index=0, target_index=0))

    assert len(state.players[0].board) == 0
    assert len(state.players[1].board) == 0
    print("test_attack_kills_both_when_equal passed")


def test_attack_only_kills_weaker():
    state = make_empty_state(
        p0_board=[make_minion(5, 5)],
        p1_board=[make_minion(3, 3)],
    )

    e.apply_move(state, m.Attack(attacker_index=0, target_index=0))

    assert len(state.players[0].board) == 1
    assert state.players[0].board[0].health == 2
    assert len(state.players[1].board) == 0
    print("test_attack_only_kills_weaker passed")


def test_attack_hero_reduces_hp():
    state = make_empty_state(p0_board=[make_minion(4, 4)], p1_hp=20)

    e.apply_move(state, m.AttackHero(attacker_index=0))

    assert state.players[1].hp == 16
    print("test_attack_hero_reduces_hp passed")


def test_attack_hero_lethal_sets_winner():
    state = make_empty_state(p0_board=[make_minion(20, 20)], p1_hp=5)

    e.apply_move(state, m.AttackHero(attacker_index=0))

    assert state.winner == 0
    print("test_attack_hero_lethal_sets_winner passed")


def test_hero_power_heals_friendly_hero():
    state = make_empty_state(p0_hp=10, p0_mana=10)

    e.apply_move(state, m.HeroPower(target=m.FriendlyHero()))

    assert state.players[0].hp == 12
    assert state.players[0].mana == 8
    assert state.players[0].hero_power_used is True
    print("test_hero_power_heals_friendly_hero passed")


def test_hero_power_caps_at_max_hp():
    state = make_empty_state(p0_hp=19, p0_mana=10)

    e.apply_move(state, m.HeroPower(target=m.FriendlyHero()))

    assert state.players[0].hp == 20
    print("test_hero_power_caps_at_max_hp passed")


def test_end_turn_switches_player():
    state = make_empty_state(current_player=0)

    e.apply_move(state, m.EndTurn())

    assert state.current_player == 1
    print("test_end_turn_switches_player passed")


def test_end_turn_clears_summoning_sickness():
    state = make_empty_state(
        p1_board=[make_minion(3, 3, can_attack=False)],
        current_player=0,
    )

    e.apply_move(state, m.EndTurn())

    assert state.players[1].board[0].can_attack is True
    print("test_end_turn_clears_summoning_sickness passed")


def test_apply_move_then_undo_restores_state():
    """v2 replacement for the old 'does not mutate input' test.
    The whole point is that we mutate -- but undo restores."""
    card_name = c.CardName.ACOLYTE_OF_PAIN
    state = make_empty_state(p0_hand=[card_name], p0_mana=10)

    assert_round_trip(state, m.PlayMinion(hand_index=0, board_position=0),
                      label="PlayMinion round-trip")
    print("test_apply_move_then_undo_restores_state passed")


def test_doomsayer_wipes_on_start_of_turn():
    state = make_empty_state(
        p0_board=[make_minion(3, 3)],
        p1_board=[make_minion(0, 7, card=c.CardName.DOOMSAYER, can_attack=False)],
        current_player=0,
    )

    e.apply_move(state, m.EndTurn())

    assert state.players[0].board == []
    assert state.players[1].board == []
    print("test_doomsayer_wipes_on_start_of_turn passed")


def test_alexstrasza_hp_and_dmg():
    state = make_empty_state(
        p0_hand=[c.CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE],
        p0_mana=10, p0_hp=10, p1_hp=29,
        current_player=0,
    )

    e.apply_move(state, m.PlayMinion(hand_index=0, board_position=0))
    assert state.players[0].hp == 15, (
        f"expected 15, got {state.players[0].hp}"
    )

    state.players[0].hero_power_power = 100
    e.apply_move(state, m.HeroPower(target=m.FriendlyHero()))
    assert state.players[1].hp == 14, (
        f"expected 14, got {state.players[1].hp}"
    )
    print("test_alexstrasza_hp_and_dmg passed")


# ----------------------------------------------------------------------
# Round-trip tests (apply + undo, assert restored)
# ----------------------------------------------------------------------

def test_round_trip_attack_both_die():
    state = make_empty_state(
        p0_board=[make_minion(3, 3)],
        p1_board=[make_minion(3, 3)],
    )
    assert_round_trip(state, m.Attack(0, 0), label="attack both die")
    print("test_round_trip_attack_both_die passed")


def test_round_trip_attack_attacker_dies():
    state = make_empty_state(
        p0_board=[make_minion(1, 1)],
        p1_board=[make_minion(5, 5)],
    )
    assert_round_trip(state, m.Attack(0, 0), label="attack attacker dies")
    print("test_round_trip_attack_attacker_dies passed")


def test_round_trip_attack_target_dies():
    state = make_empty_state(
        p0_board=[make_minion(5, 5)],
        p1_board=[make_minion(1, 1)],
    )
    assert_round_trip(state, m.Attack(0, 0), label="attack target dies")
    print("test_round_trip_attack_target_dies passed")


def test_round_trip_attack_both_survive():
    state = make_empty_state(
        p0_board=[make_minion(2, 5)],
        p1_board=[make_minion(2, 5)],
    )
    assert_round_trip(state, m.Attack(0, 0), label="attack both survive")
    print("test_round_trip_attack_both_survive passed")


def test_round_trip_attack_hero():
    state = make_empty_state(p0_board=[make_minion(4, 4)], p1_hp=20)
    assert_round_trip(state, m.AttackHero(attacker_index=0), label="attack hero")
    print("test_round_trip_attack_hero passed")


def test_round_trip_hero_power():
    state = make_empty_state(p0_hp=10, p0_mana=10)
    assert_round_trip(state, m.HeroPower(target=m.FriendlyHero()), label="hero power friendly")
    print("test_round_trip_hero_power passed")


def test_round_trip_doomsayer():
    state = make_empty_state(
        p0_board=[make_minion(3, 3)],
        p1_board=[make_minion(0, 7, card=c.CardName.DOOMSAYER, can_attack=False)],
        current_player=0,
    )
    assert_round_trip(state, m.EndTurn(), label="end turn with doomsayer")
    print("test_round_trip_doomsayer passed")


def test_round_trip_alexstrasza_battlecry():
    state = make_empty_state(
        p0_hand=[c.CardName.ALEXSTRASZA_GUARDIAN_OF_LIFE],
        p0_mana=10, p0_hp=10,
        current_player=0,
    )
    assert_round_trip(state, m.PlayMinion(hand_index=0, board_position=0),
                      label="play alexstrasza")
    print("test_round_trip_alexstrasza_battlecry passed")

def play_all_spells():
    from game.cards import Spell_test
    from bots.sampling_bot_V2 import Sampling_Bot_V2 as s
    s1 = s()
    s2= s()
    bot_tuple={}
    state = make_empty_state(
        p0_deck=Spell_test,
        p1_deck=Spell_test,
        p0_hp=20000000,
        p1_hp=20000000,
    )
    while not state.winner:
        for p in bot_tuple:
            next_move = bot_tuple[p].pick_move(state)
            print(f"MOVE:{next_move}")
            apply_move(next_move)



from game.engine import new_game, apply_move, _start_turn
from game.moves import EndTurn
from game.cards import CardName
from bots.sample_bot_v3.sample_bot import Sampling_Bot_V3


state = new_game(seed=42)
# Force the scenario: give the opponent a Doomsayer on board
# (set up state manually so you KNOW what should happen)

print("BEFORE my turn starts:")
print(f"  cp={state.current_player}")
print(f"  opp board: {[m.card for m in state.players[...].board]}")

# Now manually do what sim_opps_turn's EndTurn would do:
undo = apply_move(state, EndTurn())

print("AFTER opponent's EndTurn (which should start MY turn):")
print(f"  cp={state.current_player}")
print(f"  my board: {[m.card for m in state.players[...].board]}")
# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------

def run_all_tests():
    tests = [
        # Forward-only tests (assert state after apply)
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
        test_apply_move_then_undo_restores_state,
        test_doomsayer_wipes_on_start_of_turn,
        test_alexstrasza_hp_and_dmg,

        # Round-trip tests
        test_round_trip_attack_both_die,
        test_round_trip_attack_attacker_dies,
        test_round_trip_attack_target_dies,
        test_round_trip_attack_both_survive,
        test_round_trip_attack_hero,
        test_round_trip_hero_power,
        test_round_trip_doomsayer,
        test_round_trip_alexstrasza_battlecry,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as ex:
            print(f"FAIL {test.__name__}: {ex}")
            failed += 1
        except Exception as ex:
            print(f"CRASH {test.__name__}: {type(ex).__name__}: {ex}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")


if __name__ == "__main__":
    run_all_tests()
