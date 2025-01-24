from dataclasses import dataclass, field
from typing import Generator
import json


from quantikai.game.exceptions import InvalidMoveError
from quantikai.game.enums import Colors, Pawns
from quantikai.game.move import Move


@dataclass(frozen=True, eq=True)
class FrozenBoard:
    board: tuple[tuple[tuple[Pawns, Colors] | None]]


class Board:
    board: list[list[tuple[Pawns, Colors] | None]]

    def __init__(self, board=None):
        if board is not None:
            assert len(board) == 4 and len(board[0]) == 4
            self.board = [[elt for elt in row] for row in board]
        else:
            self.board = [[None for _ in range(4)] for _ in range(4)]

    @classmethod
    def from_json(cls, body: list[list[tuple[str, str] | None]]):
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

    def play(self, move: Move):
        self._check_move_is_valid(move)
        self.board[move.x][move.y] = (move.pawn, move.color)
        return self._move_is_a_win(move.x, move.y)

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
                        self._check_move_is_valid(Move(x, y, pawn, color))
                        return True
                    except InvalidMoveError:
                        pass
        return False

    def get_possible_moves(
        self, pawns: list[Pawns], color: Colors, optimize=False
    ) -> set[Move]:
        """_summary_

        Args:
            pawns (list[Pawns]): _description_
            color (Colors): _description_
            optimize (bool, optional): if True, does not return equivalent moves (to optimize computation of the next best move). Defaults to False.

        Returns:
            set[Move]: _description_
        """
        board_len = len(self.board)
        if optimize:
            pawns_on_board: set[Move] = set()
            for x in range(board_len):
                for y in range(board_len):
                    if self.board[x][y] is not None:
                        pawns_on_board.add(
                            Move(x, y, self.board[x][y][0], self.board[x][y][1])
                        )
            # Case 1: No pawn on the board
            if len(pawns_on_board) == 0:
                # Only need to check for one pawn and one section because of symmetry
                # Actually I am not even sure the first move matters
                return {
                    Move(0, 0, Pawns.A, color),
                    Move(0, 1, Pawns.A, color),
                    Move(1, 0, Pawns.A, color),
                    Move(1, 1, Pawns.A, color),
                }
            # Case 2: 1 pawn on the board
            # Diagonal symmetry: both sections next to the played section are the same and in opposite section 2 cells are
            # the same
            # Pawn: either play the same pawn or a different one. If different, does not matter which one
            if len(pawns_on_board) == 1:
                # x, y, pawn, _ = pawns_on_board.pop()
                cell_pawn = pawns_on_board.pop()
                other_pawn = [p for p in Pawns if p != cell_pawn.pawn][0]
                return (
                    {
                        # other pawn, same section
                        Move(i, j, other_pawn, color)
                        for (i, j) in self._get_section_elements(
                            cell_pawn.x, cell_pawn.y
                        )
                        if (i, j) != (cell_pawn.x, cell_pawn.y)
                    }
                    | {
                        # other pawn, adjacent section
                        Move(i, j, other_pawn, color)
                        for (i, j) in self._get_section_elements(
                            (cell_pawn.x + 2) % 4, cell_pawn.y
                        )
                    }
                    | {
                        # same pawn, adjacent section (only 2 possible positions)
                        Move(i, j, cell_pawn.pawn, color)
                        for (i, j) in self._get_section_elements(
                            (cell_pawn.x + 2) % 4, cell_pawn.y
                        )
                        if i != cell_pawn.x and j != cell_pawn.y
                    }
                    | {
                        # same or other pawn, opposite section
                        Move(i, j, p, color)
                        for p in [cell_pawn.pawn, other_pawn]
                        for i, j in self._get_section_elements(
                            (cell_pawn.x + 2) % 4, (cell_pawn.y + 2) % 4
                        )
                    }
                )
        # Get all possible moves
        moves: set = {
            (x, y, pawn, color)
            for x in range(board_len)
            for y in range(board_len)
            for pawn in pawns
        }
        for x in range(board_len):
            for y in range(board_len):
                if self.board[x][y] is not None:
                    for pawn in pawns:
                        moves.discard((x, y, pawn, color))
                    if self.board[x][y][1] != color:
                        opponent_pawn: Pawns = self.board[x][y][0]
                        for idx in range(board_len):
                            moves.discard((idx, y, opponent_pawn, color))
                            moves.discard((x, idx, opponent_pawn, color))
                        for i, j in self._get_section_elements(x, y):
                            moves.discard((i, j, opponent_pawn, color))
        # Optimization: from 90s to 59s by using tuples instead of Move in the previous steps
        return {Move(*item) for item in moves}

    def get_frozen(self) -> FrozenBoard:
        board_len = len(self.board)
        return FrozenBoard(
            tuple(
                tuple(self.board[x][y] for y in range(board_len))
                for x in range(board_len)
            )
        )

    def _check_move_is_valid(self, move: Move):
        if (
            move.x < 0
            or move.y < 0
            or move.x >= len(self.board)
            or move.y >= len(self.board[0])
        ):
            raise InvalidMoveError(
                "x and y must be between 0 and 4, their values are: "
                + str(move.x)
                + " "
                + str(move.y)
            )
        if self.board[move.x][move.y]:
            raise InvalidMoveError("already a pawn there")
        for element in self.board[move.x]:
            if element and element[0] == move.pawn and element[1] != move.color:
                raise InvalidMoveError("there is an opponent's pawn in that row")
        for row in self.board:
            if (
                row[move.y]
                and row[move.y][0] == move.pawn
                and row[move.y][1] != move.color
            ):
                raise InvalidMoveError("there is an opponent's pawn in that column")
        # check section
        for i, j in self._get_section_elements(move.x, move.y):
            if (
                self.board[i][j] is not None
                and self.board[i][j][0] == move.pawn
                and self.board[i][j][1] != move.color
            ):
                raise InvalidMoveError("there is an opponent's pawn in that section")

    def _move_is_a_win(self, x: int, y: int):
        return self._row_win(x) or self._column_win(y) or self._section_win(x, y)

    def _ctxt(self, txt: str, color: Colors | None = None) -> str:
        if color == "BLUE":
            return "\033[44m" + txt + "\033[0m"
        if color == "RED":
            return "\033[41m" + txt + "\033[0m"

    def _row_win(self, x: int):
        others: set[Pawns] = set()
        for element in self.board[x]:
            if not element or element[0] in others:
                return False
            others.add(element[0])
        return True

    def _column_win(self, y: int):
        others: set[Pawns] = set()
        for row in self.board:
            if row[y] is None or row[y][0] in others:
                return False
            others.add(row[y][0])
        return True

    def _section_win(self, x: int, y: int):
        others: set[Pawns] = set()
        for i, j in self._get_section_elements(x, y):
            if self.board[i][j] is None or self.board[i][j][0] in others:
                return False
            others.add(self.board[i][j][0])
        return True

    def _get_section_elements(
        self, x: int, y: int
    ) -> Generator[tuple[int, int], None, None]:

        yield from (
            (i, j)
            for i in range(2 * (x // 2), 2 * (x // 2 + 1))
            for j in range(2 * (y // 2), 2 * (y // 2 + 1))
        )
