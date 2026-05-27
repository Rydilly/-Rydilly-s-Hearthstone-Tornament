from dataclasses import dataclass, field
from typing import Optional
from game import cards
import numpy


@dataclass(slots=True)
class Minion:
    """
    A minion on the board with dynamic stats.
    """
    card: cards.CardName
    attack: int
    health: int
    max_health: int
    taunt: bool
    can_attack: bool


@dataclass(slots=True)
class PlayerState:
    alexstrasza_guardian_of_life_charges:int = 0
    hp: int = 30
    max_hp: int = 30
    mana: int = 0
    max_mana: int = 0
    hand: list[cards.CardName] = field(default_factory=list)
    deck: list[cards.CardName] = field(default_factory=list)
    board: list[Minion] = field(default_factory=list)
    fatigue_counter: int = 0
    hero_power_used: bool = False
    hero_power_power: int = 2

    def encode_minions(self)->numpy.ndarray:
        """
        makes vectors representing all minions on players board
        """

        features = []

        for mn in self.board:
            health_ratio = mn.health/mn.max_health
            attack_ratio = mn.attack/mn.health

            features.append([
                mn.attack,
                mn.health,
                mn.max_health,
                1.0 if mn.taunt else 0.0,
                1.0 if mn.can_attack else 0.0,
                health_ratio,
                attack_ratio
            ])

        return numpy.array(features, dtype=numpy.float32)


@dataclass(slots=True)
class GameState:
    players: tuple[PlayerState, PlayerState]
    current_player: int
    turn_number: int = 1
    winner: Optional[int] = None


    def state_key(self):
        p:PlayerState = self.players[self.current_player]
        o:PlayerState = self.players[1-self.current_player]
        return (
            #p.hp,p.mana,p.hero_power_used,
            #tuple(p.hand),
            #tuple(p.deck),#dont need for minion with no spells ond no ability version
            p.alexstrasza_guardian_of_life_charges,
            p.hp,
            p.max_hp,
            p.mana,
            p.hero_power_used,
            p.hero_power_power,
            tuple(sorted(card.value for card in p.hand)),#all the data each card holds when outcast is implemented needs changed
            tuple((m.attack,m.health) for m in p.board),#windfurry will need more data when added
            o.hp,
            o.fatigue_counter,
            tuple((m.attack,m.health,m.taunt)for m in o.board)
        )

    def __repr__(self) -> str:
        if self.winner is not None:
            return f"<Game over, winner={self.winner}>"
        lines = [f"=== Turn {self.turn_number}, P{self.current_player}'s turn ==="]
        for i, p in enumerate(self.players):
            marker = "*" if i == self.current_player else " "
            lines.append(
                f"{marker}P{i}: HP={p.hp}/{p.max_hp} Mana={p.mana}/{p.max_mana} "
                f"Hand={len(p.hand)} Deck={len(p.deck)}"
            )
            if p.board:
                board_str = " ".join(
                    f"[{m.attack}/{m.health}{'T' if m.taunt else ''}{'' if m.can_attack else '~'}]"
                    for m in p.board
                )
                lines.append(f"   Board: {board_str}")
            else:
                lines.append(f"   Board: (empty)")
        return "\n".join(lines)


    def render(self) -> str:
            """Multi-line human-readable view. Call explicitly."""
            if self.winner is not None:
                return f"=== Game over, winner=P{self.winner} ==="
            lines = [f"=== Turn {self.turn_number}, P{self.current_player}'s turn ==="]
            for i, p in enumerate(self.players):
                marker = "*" if i == self.current_player else " "
                lines.append(
                    f"{marker}P{i}: HP={p.hp}/{p.max_hp} Mana={p.mana}/{p.max_mana} "
                    f"Hand={len(p.hand)} Deck={len(p.deck)}"
                )
                if p.board:
                    board_str = " ".join(
                        f"[{m.attack}/{m.health}{'T' if m.taunt else ''}{'' if m.can_attack else '~'}]"
                        for m in p.board
                    )
                    lines.append(f"   Board: {board_str}")
                else:
                    lines.append(f"   Board: (empty)")
            return "\n".join(lines)