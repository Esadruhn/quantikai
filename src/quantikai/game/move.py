from dataclasses import dataclass

from quantikai.game.enums import Colors, Pawns


@dataclass(frozen=True)
class Move:
    x: int
    y: int
    pawn: Pawns
    color: Colors

    def to_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "pawn": self.pawn.name,
            "color": self.color.name,
        }
