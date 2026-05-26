from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from game import cards

@dataclass
class Minion:
    """
    A minion on the board with dynamic stats
    """
    card: cards.CardName
    attack: int
    health: int
    max_health: int
    taunt: bool
    can_attack: bool

@dataclass
class PlayerState:
    hero_power_used: bool = False
    hero_power_power: int = 2
    hp: int = 20
    max_hp: int = 20
    mana: int = 0
    max_mana: int = 0
    hand: list[cards.CardName]= field(default_factory=list)#the int is the turn the card was put in hand
    deck: list[cards.CardName]=field(default_factory=list)
    board: list[Minion]=field(default_factory=list)
    fatigue_counter: int = 0

@dataclass
class GameState:
    players: tuple[PlayerState, PlayerState]
    current_player: int #0 or 1 for player 1 or 2's turn
    turn_number: int=1
    winner: Optional[int] = None



