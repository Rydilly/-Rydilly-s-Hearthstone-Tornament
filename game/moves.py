from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class FriendlyHero:
    pass


@dataclass(frozen=True)
class EnemyHero:
    pass


@dataclass(frozen=True)
class FriendlyMinion:
    index: int


@dataclass(frozen=True)
class EnemyMinion:
    index: int


Target = Union[FriendlyHero, EnemyHero, FriendlyMinion, EnemyMinion]


@dataclass(frozen=True)
class PlayMinion:
    hand_index: int
    board_position: int

@dataclass(frozen=True)
class PlaySpell:
    hand_index: int
    target: Target|None


@dataclass(frozen=True)
class Attack:
    attacker_index: int
    target_index: int


@dataclass(frozen=True)
class AttackHero:
    attacker_index: int


@dataclass(frozen=True)
class HeroPower:
    target: Target


@dataclass(frozen=True)
class EndTurn:
    pass


Move = Union[PlayMinion, Attack, AttackHero, HeroPower, EndTurn]
