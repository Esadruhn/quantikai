from dataclasses import dataclass, field
from typing import Generator
import json

from quantikai.game.exceptions import InvalidMoveError
from quantikai.game.enums import Colors, Pawns
from quantikai.game.player import Player


@dataclass(frozen=True, eq=True)
class FrozenBoard:
    board: tuple[tuple[Pawns, Colors]]


@dataclass
class Board:
    board: list[list[tuple[Pawns, Colors]]] = field(
        default_factory=lambda: [[None for _ in range(4)] for _ in range(4)]
    )

    @classmethod
    def from_json(cls, body):
        # TODO check values in body
        return cls(
            board=[
                [
                    None if elt is None else (Pawns[elt[0]], Colors[elt[1]])
                    for elt in row
                ]
                for row in body
            ]
        )

    def to_json(self):
        return [
            [None if v is None else (v[0].name, v[1].name) for v in row]
            for row in self.board
        ]

    def play(self, x: int, y: int, pawn: Pawns, color: Colors):
        pawn = Pawns(pawn)
        color = Colors(color)
        self._check_move_is_valid(x, y, pawn, color)
        self.board[x][y] = (pawn, color)
        return self._move_is_a_win(x, y)

    def print(self):
        upper_idx = "  "
        for x in range(0, 4):
            upper_idx += "   " + str(x) + "  "
        upper_idx += "\n"
        upper_separator = "  " + " ____ " * 2 + "  " + "____  " * 2 + "\n"
        str_board = upper_idx + upper_separator
        for i in range(4):
            str_board += str(i) + " "
            for j in range(4):
                if self.board[i][j]:
                    str_board += self._ctxt(
                        "|__" + self.board[i][j][0].value + "_|", self.board[i][j][1]
                    )
                else:
                    str_board += "|____|"
                if j + 1 == 2:
                    str_board += " "
            str_board += "\n"
            if i + 1 == 2:
                str_board += upper_separator

        print(str_board)

    def have_possible_move(self, color: Colors):
        for x, row in enumerate(self.board):
            for y, _ in enumerate(row):
                for pawn in Pawns:
                    try:
                        self._check_move_is_valid(x, y, pawn, color)
                        return True
                    except InvalidMoveError:
                        pass
        return False

    def get_possible_moves(
        self, pawns: list[Pawns], color: Colors, optimize=False
    ) -> set[tuple[int, int, Pawns, Colors]]:
        """_summary_

        Args:
            pawns (list[Pawns]): _description_
            color (Colors): _description_
            optimize (bool, optional): if True, does not return equivalent moves (to optimize computation of the next best move). Defaults to False.

        Returns:
            set[tuple[int, int, Pawns, Colors]]: _description_
        """
        if optimize:
            pawns_on_board = set()
            for x in range(len(self.board)):
                for y in range(len(self.board)):
                    if self.board[x][y] is not None:
                        pawns_on_board.add(
                            (x, y, self.board[x][y][0], self.board[x][y][1])
                        )
            # Case 1: No pawn on the board
            if len(pawns_on_board) == 0:
                # Only need to check for one pawn and one section because of symmetry
                # Actually I am not even sure the first move matters
                return {
                    (0, 0, Pawns.A, color),
                    (0, 1, Pawns.A, color),
                    (1, 0, Pawns.A, color),
                    (1, 1, Pawns.A, color),
                }
            # Case 2: 1 pawn on the board
            # Diagonal symmetry: both sections next to the played section are the same and in opposite section 2 cells are
            # the same
            # Pawn: either play the same pawn or a different one. If different, does not matter which one
            if len(pawns_on_board) == 1:
                x, y, pawn, _ = pawns_on_board.pop()
                other_pawn = [x for x in Pawns if x != pawn][0]
                return (
                    {
                        # other pawn, same section
                        (i, j, other_pawn, color)
                        for (i, j) in self._get_section_elements(x, y)
                        if (i, j) != (x, y)
                    }
                    | {
                        # other pawn, adjacent section
                        (i, j, other_pawn, color)
                        for (i, j) in self._get_section_elements((x + 2) % 4, y)
                    }
                    | {
                        # same pawn, adjacent section (only 2 possible positions)
                        (i, j, pawn, color)
                        for (i, j) in self._get_section_elements((x + 2) % 4, y)
                        if i != x and j != y
                    }
                    | {
                        # same or other pawn, opposite section
                        # TODO: we could remove one more cell in this section (diag sym)
                        (i, j, p, color)
                        for p in [pawn, other_pawn]
                        for i, j in self._get_section_elements((x + 2) % 4, (y + 2) % 4)
                    }
                )

        # Get all possible moves
        moves = {
            (x, y, pawn, color)
            for x in range(len(self.board))
            for y in range(len(self.board))
            for pawn in pawns
        }
        opponent_color = [c for c in Colors if c != color][0]
        for x in range(len(self.board)):
            for y in range(len(self.board)):
                if self.board[x][y] is not None:
                    moves -= {(x, y, pawn, color) for pawn in pawns}
                    if self.board[x][y][1] == opponent_color:
                        opponent_pawn = self.board[x][y][0]
                        moves -= {
                            (i, y, opponent_pawn, color) for i in range(len(self.board))
                        }
                        moves -= {
                            (x, j, opponent_pawn, color) for j in range(len(self.board))
                        }
                        moves -= {
                            (i, j, opponent_pawn, color)
                            for i, j in self._get_section_elements(x, y)
                        }
        return moves

    def get_frozen(self) -> FrozenBoard:
        return FrozenBoard(
            tuple(
                tuple(self.board[x][y] for y in range(len(self.board)))
                for x in range(len(self.board))
            )
        )

    def _check_move_is_valid(self, x: int, y: int, pawn: Pawns, player: Colors):
        if x < 0 or y < 0 or x >= len(self.board) or y >= len(self.board[0]):
            raise InvalidMoveError(
                "x and y must be between 0 and "
                + str(4)
                + " their values are: "
                + str(x)
                + " "
                + str(y)
            )
        if self.board[x][y]:
            raise InvalidMoveError("already a pawn there")
        for element in self.board[x]:
            if element and element[0] == pawn and element[1] != player:
                raise InvalidMoveError("there is an opponent's pawn in that row")
        for row in self.board:
            if row[y] and row[y][0] == pawn and row[y][1] != player:
                raise InvalidMoveError("there is an opponent's pawn in that column")
        # check section
        for row in self.board[2 * (x // 2) : 2 * (x // 2 + 1)]:
            for element in row[2 * (y // 2) : 2 * (y // 2 + 1)]:
                if element and element[0] == pawn and element[1] != player:
                    raise InvalidMoveError(
                        "there is an opponent's pawn in that section"
                    )

    def _move_is_a_win(self, x: int, y: int):
        return self._row_win(x) or self._column_win(y) or self._section_win(x, y)

    def _ctxt(self, txt: str, color: Colors = None) -> str:
        if color:
            txt = color.value + txt + "\033[0m"
        return txt

    def _row_win(self, x: int):
        others = set()
        for element in self.board[x]:
            if not element or element[0] in others:
                return False
            others.add(element[0])
        return True

    def _column_win(self, y: int):
        others = set()
        for row in self.board:
            if not row[y] or row[y][0] in others:
                return False
            others.add(row[y][0])
        return True

    def _section_win(self, x: int, y: int):
        others = set()
        for i, j in self._get_section_elements(x, y):
            element = self.board[i][j]
            if not element or element[0] in others:
                return False
            others.add(element[0])
        return True

    def _get_section_elements(
        self, x: int, y: int
    ) -> Generator[tuple[int, int], None, None]:
        def lower(z):
            return 2 * (z // 2)

        def upper(z):
            return 2 * (z // 2 + 1)

        for i in range(lower(x), upper(x)):
            for j in range(lower(y), upper(y)):
                yield i, j
