from dataclasses import dataclass

from quantikai.game.enums import Colors, Pawns


@dataclass(frozen=True)
class Move:
    x: int
    y: int
    pawn: Pawns
    color: Colors

    # TODO
    def to_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "pawn": self.pawn.name,
            "color": self.color.name,
        }

    def to_compressed(self):
        return [self.x, self.y, self.pawn.name, self.color.name]

    @classmethod
    def from_compressed(cls, body):
        if body is None:
            return None
        return cls(x=body[0], y=body[1], pawn=Pawns[body[2]], color=Colors[body[3]])
