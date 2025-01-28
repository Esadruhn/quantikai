from dataclasses import dataclass, asdict

from quantikai.game import FrozenBoard, Move


@dataclass(frozen=True, eq=True)
class Node:
    """Hashable class to represent a node in a tree representation of the game.
    A node is a state of the board and a move_to_play to apply to the board.
    For the initial state of the game move_to_play is None.
    """

    board: FrozenBoard
    move_to_play: Move | None = None

    def to_json(self):
        return {
            "board": self.board.to_json(),
            "move_to_play": (
                None if self.move_to_play is None else self.move_to_play.to_json()
            ),
        }

    def to_compressed(self):
        return [
            self.board.to_compressed(),
            None if self.move_to_play is None else self.move_to_play.to_compressed(),
        ]

    @classmethod
    def from_compressed(cls, body):
        return cls(
            board=FrozenBoard.from_compressed(body[0]),
            move_to_play=Move.from_compressed(body[1]),
        )
