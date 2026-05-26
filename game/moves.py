from dataclasses import dataclass
from typing import Union
from game import state, cards

@dataclass(frozen=True)
class FriendlyHero: 
    pass

@dataclass (frozen = True)
class EnemyHero: 
    pass

@dataclass(frozen = True)
class FriendlyMinion:
    pass

@dataclass(frozen = True)
class EnemyMinion:
    pass

Target = Union[FriendlyHero, EnemyHero, FriendlyMinion, EnemyMinion]


@dataclass(frozen = True)
class PlayMinion:
    hand_index: int
    board_position: int

@dataclass(frozen=True)
class Attack:
    attacker_index: int
    target_index: int

@dataclass(frozen=True)
class AttackHero:
    attacker_index: int

@dataclass(frozen=True)
class EndTurn:
    pass

@dataclass(frozen=True)
class HeroPower:
    target_index: int

Move = Union[PlayMinion, Attack, HeroPower, EndTurn, AttackHero]

