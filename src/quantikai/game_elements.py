"""Main module."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Generator

NB_CELLS = 2


class Pawns(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Colors(Enum):
    BLUE = "\033[44m"
    RED = "\033[41m"


class InvalidMoveError(Exception):
    def __init__(self, message):
        super().__init__(message)


@dataclass
class Player:
    color: Colors
    pawns: list[Pawns] = field(
        default_factory=lambda: NB_CELLS * [pawn for pawn in Pawns]
    )

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


@dataclass
class Board:
    board: list[list[tuple[Pawns, Colors]]] = field(
        default_factory=lambda: [[None for _ in range(4)] for _ in range(4)]
    )

    def play(self, x: int, y: int, pawn: Pawns, color: Colors):
        pawn = Pawns(pawn)
        color = Colors(color)
        self._check_move_is_valid(x, y, pawn, color)
        self.board[x][y] = (pawn, color)
        return self._move_is_a_win(x, y)

    def print(self):
        upper_idx = "  "
        for x in range(0, NB_CELLS * 2):
            upper_idx += "   " + str(x) + "  "
        upper_idx += "\n"
        upper_separator = "  " + " ____ " * NB_CELLS + "  " + "____  " * NB_CELLS + "\n"
        str_board = upper_idx + upper_separator
        for i in range(NB_CELLS * 2):
            str_board += str(i) + " "
            for j in range(NB_CELLS * 2):
                if self.board[i][j]:
                    str_board += self._ctxt(
                        "|__" + self.board[i][j][0].value + "_|", self.board[i][j][1]
                    )
                else:
                    str_board += "|____|"
                if j + 1 == NB_CELLS:
                    str_board += " "
            str_board += "\n"
            if i + 1 == NB_CELLS:
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
            optimize (bool, optional): if True, does not return equivalent
                moves (to optimize computation of the next best move).
                Defaults to False.

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
                # return {
                #     (0, 0, Pawns.A, color),
                #     (0, 1, Pawns.A, color),
                #     (1, 0, Pawns.A, color),
                #     (1, 1, Pawns.A, color),
                # }
                # TODO: check if this makes sense
                return {(1, 1, Pawns.A, color)}
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

    def _check_move_is_valid(self, x: int, y: int, pawn: Pawns, player: Colors):
        if x < 0 or y < 0 or x >= len(self.board) or y >= len(self.board[0]):
            raise InvalidMoveError(
                "x and y must be between 0 and " + str(NB_CELLS * NB_CELLS)
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
        for row in self.board[
            NB_CELLS * (x // NB_CELLS) : NB_CELLS * (x // NB_CELLS + 1)
        ]:
            for element in row[
                NB_CELLS * (y // NB_CELLS) : NB_CELLS * (y // NB_CELLS + 1)
            ]:
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
            return NB_CELLS * (z // NB_CELLS)

        def upper(z):
            return NB_CELLS * (z // NB_CELLS + 1)

        for i in range(lower(x), upper(x)):
            for j in range(lower(y), upper(y)):
                yield i, j
