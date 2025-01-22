from dataclasses import dataclass, field

from quantikai.game.exceptions import InvalidMoveError
from quantikai.game.enums import Colors, Pawns


@dataclass
class Player:
    color: Colors
    pawns: list[Pawns] = field(default_factory=lambda: 2 * [pawn for pawn in Pawns])

    def remove(self, pawn: Pawns):
        self.check_has_pawn(pawn)
        self.pawns.remove(pawn)

    def check_has_pawn(self, pawn):
        if not pawn in self.pawns:
            raise InvalidMoveError("You do not have this pawn.")

    def get_printable_list_pawns(self):
        t = ""
        for pawn in self.pawns:
            t += pawn.value + " "
        return "Player " + self.color.name + " available pawns: " + t

    @classmethod
    def from_json(cls, body):
        # TODO check values in body
        return cls(color=Colors[body["color"]], pawns=[Pawns(p) for p in body["pawns"]])

    def to_json(self):
        return {"color": self.color.name, "pawns": [p.name for p in self.pawns]}
