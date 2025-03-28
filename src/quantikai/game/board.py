from dataclasses import dataclass
from typing import Generator

from quantikai.game.enums import Colors, Pawns
from quantikai.game.exceptions import InvalidMoveError
from quantikai.game.move import Move


@dataclass(frozen=True, eq=True)
class FrozenBoard:
    board: frozenset[tuple[int, int, Pawns, Colors]]

    def __len__(self):
        return len(self.board)

    def items(self):
        for item in self.board:
            yield item

    def to_json(self):
        return list(self.board)

    def to_compressed(self):
        return list(self.board)

    @classmethod
    def from_compressed(cls, body):
        return cls(
            frozenset(
                {
                    (
                        int(item[0]),
                        int(item[1]),
                        Pawns[item[2]],
                        Colors[item[3]],
                    )
                    for item in body
                }
            )
        )


class Board:
    _board: dict[tuple[int, int], tuple[Pawns, Colors]]
    _size: int = 4

    def __init__(
        self,
        board: (
            FrozenBoard | dict[tuple[int, int], tuple[Pawns, Colors]] | None
        ) = None,
    ):
        if board is not None:
            if isinstance(board, FrozenBoard):
                self._board = {(x, y): (p, c) for x, y, p, c in board.items()}
            elif isinstance(board, dict):
                self._board = board
            else:
                # TODO
                raise
        else:
            self._board = dict()

    def __len__(self):
        return len(self._board)

    @classmethod
    def from_json(cls, body: list[list[tuple[str, str] | None]]):
        return cls(
            board={
                (x, y): (Pawns[body[x][y][0]], Colors[body[x][y][1]])
                for x in range(cls._size)
                for y in range(cls._size)
                if body[x][y] is not None
            }
        )

    def to_json(self) -> list[list[tuple[str, str] | None]]:
        return [
            [
                (
                    (
                        self._board[(row_nb, col_nb)][0].name,
                        self._board[(row_nb, col_nb)][1].name,
                    )
                    if (row_nb, col_nb) in self._board
                    else None
                )
                for col_nb in range(self._size)
            ]
            for row_nb in range(self._size)
        ]

    def play(self, move: Move, strict: bool = True):
        if strict:
            self._check_move_is_valid(move)
        self._board[(move.x, move.y)] = (move.pawn, move.color)
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
                if (i, j) in self._board:
                    str_board += self._ctxt(
                        "|__" + self._board[(i, j)][0].value + "_|",
                        self._board[(i, j)][1],
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
        for x in range(self._size):
            for y in range(self._size):
                for pawn in Pawns:
                    try:
                        self._check_move_is_valid(Move(x, y, pawn, color))
                        return True
                    except InvalidMoveError:
                        pass
        return False

    def get_possible_moves(
        self, pawns: list[Pawns], color: Colors, optimize=False
    ):
        """_summary_

        Args:
            pawns (list[Pawns]): _description_
            color (Colors): _description_
            optimize (bool, optional): if True, does not return equivalent moves (to optimize computation of the next best move). Defaults to False.

        Returns:
            set[Move]: _description_
        """
        moves = set()
        conditions = list()
        if optimize:
            # playable pawns are those already on board + one unknown
            pawns_on_board = {p for p, _ in self._board.values() if p in pawns}
            extra_pawns = set(pawns) - pawns_on_board
            pawns = list(pawns_on_board)
            if len(extra_pawns) > 0:
                pawns.append(list(extra_pawns)[0])
            if self._horizontal_symmetry() == self._board:
                conditions.append(lambda x, y: x <= 1)
            if self._vertical_symmetry() == self._board:
                conditions.append(lambda x, y: y <= 1)
            if self._diag_left_symmetry() == self._board:
                conditions.append(lambda x, y: x <= y)
            if self._diag_right_symmetry() == self._board:
                conditions.append(lambda x, y: x + y <= 3)

        moves: set = {
            (i, j, p, color)
            for i in range(self._size)
            for j in range(self._size)
            for p in pawns
        }
        for (bx, by), (bpawn, bcolor) in self._board.items():
            for pawn in pawns:
                moves.discard((bx, by, pawn, color))
            if bcolor != color:
                for idx in range(self._size):
                    moves.discard((idx, by, bpawn, color))
                    moves.discard((bx, idx, bpawn, color))
                for i, j in self._get_section_elements(bx, by):
                    moves.discard((i, j, bpawn, color))
            # Optimization: 30% speed-up using tuples instead of Move in the previous step
        for item in moves:
            if all([c(item[0], item[1]) for c in conditions]):
                yield Move(*item)
            else:
                continue

    def get_frozen(self) -> FrozenBoard:
        return FrozenBoard(
            frozenset((x, y, p, c) for (x, y), (p, c) in self._board.items())
        )

    def _check_move_is_valid(self, move: Move):
        if (
            move.x < 0
            or move.y < 0
            or move.x >= self._size
            or move.y >= self._size
        ):
            raise InvalidMoveError(
                "x and y must be between 0 and 4, their values are: "
                + str(move.x)
                + " "
                + str(move.y)
            )
        if (move.x, move.y) in self._board:
            raise InvalidMoveError("already a pawn there")
        for j in range(self._size):
            if (
                (move.x, j) in self._board
                and self._board[(move.x, j)][0] == move.pawn
                and self._board[(move.x, j)][1] != move.color
            ):
                raise InvalidMoveError(
                    "there is an opponent's pawn in that row"
                )
        for i in range(self._size):
            if (
                (i, move.y) in self._board
                and self._board[(i, move.y)][0] == move.pawn
                and self._board[(i, move.y)][1] != move.color
            ):
                raise InvalidMoveError(
                    "there is an opponent's pawn in that column"
                )
        # check section
        for i, j in self._get_section_elements(move.x, move.y):
            if (
                (i, j) in self._board
                and self._board[(i, j)][0] == move.pawn
                and self._board[(i, j)][1] != move.color
            ):
                raise InvalidMoveError(
                    "there is an opponent's pawn in that section"
                )

    def _move_is_a_win(self, x: int, y: int):
        return (
            self._row_win(x) or self._column_win(y) or self._section_win(x, y)
        )

    def _ctxt(self, txt: str, color: Colors | None = None) -> str:
        if color == "BLUE":
            return "\033[44m" + txt + "\033[0m"
        if color == "RED":
            return "\033[41m" + txt + "\033[0m"

    def _row_win(self, x: int):
        other_pawns: set[Pawns] = set()
        for j in range(self._size):
            if (
                not (x, j) in self._board
                or self._board[(x, j)][0] in other_pawns
            ):
                return False
            other_pawns.add(self._board[(x, j)][0])
        return True

    def _column_win(self, y: int):
        other_pawns: set[Pawns] = set()
        for i in range(self._size):
            if (
                not (i, y) in self._board
                or self._board[(i, y)][0] in other_pawns
            ):
                return False
            other_pawns.add(self._board[(i, y)][0])
        return True

    def _section_win(self, x: int, y: int):
        others: set[Pawns] = set()
        for i, j in self._get_section_elements(x, y):
            if not (i, j) in self._board or self._board[(i, j)][0] in others:
                return False
            others.add(self._board[(i, j)][0])
        return True

    def _get_section_elements(
        self, x: int, y: int
    ) -> Generator[tuple[int, int], None, None]:

        yield from (
            (i, j)
            for i in range(2 * (x // 2), 2 * (x // 2 + 1))
            for j in range(2 * (y // 2), 2 * (y // 2 + 1))
        )

    def _horizontal_symmetry(self) -> dict:
        return {(3 - x, y): pc for ((x, y), pc) in self._board.items()}

    def _vertical_symmetry(self) -> dict:
        return {(x, 3 - y): pc for ((x, y), pc) in self._board.items()}

    def _diag_left_symmetry(self) -> dict:
        return {(y, x): pc for ((x, y), pc) in self._board.items()}

    def _diag_right_symmetry(self) -> dict:
        return {(3 - y, 3 - x): pc for ((x, y), pc) in self._board.items()}
