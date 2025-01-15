"""Main module."""

from enum import Enum
from dataclasses import dataclass, field

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

    # Optimization: make it easier to spot possible moves
    _rows: list[set] = field(default_factory=lambda: [set() for _ in range(4)])
    _columns: list[set] = field(default_factory=lambda: [set() for _ in range(4)])
    # Sections:
    # 0 1
    # 2 3
    _sections: list[set] = field(default_factory=lambda: [set() for _ in range(4)])

    def __post_init__(self):
        for x in range(len(self.board)):
            for y in range(len(self.board)):
                if self.board[x][y] is not None:
                    self._rows[x].add(self.board[x][y])
                    self._columns[y].add(self.board[x][y])
                    sec_idx = self._get_section_idx(x,y)
                    self._sections[sec_idx].add(self.board[x][y])

    def play(self, x: int, y: int, pawn: Pawns, color: Colors):
        pawn = Pawns(pawn)
        color = Colors(color)
        self._check_move_is_valid(x, y, pawn, color)
        self.board[x][y] = (pawn, color)
        self._add_to_optimized(x,y,pawn, color)
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
                for pawn in set(Pawns):
                    try:
                        self._check_move_is_valid(x, y, pawn, color)
                        return True
                    except InvalidMoveError:
                        pass
        return False
    
    def get_possible_moves(self, pawns: list[Pawns], color: Colors) -> set[tuple[int, int, Pawns, Colors]]:
        moves = {(x, y, pawn, color) for x in range(len(self.board)) for y in range(len(self.board)) for pawn in pawns}
        opponent_color = [c for c in Colors if c != color][0]
        for x in range(len(self.board)):
            for y in range(len(self.board)):
                if self.board[x][y]:
                    moves -= {(x,y,pawn) for pawn in pawns}
                    if self.board[x][y][1] == opponent_color:
                        moves -= {(i,y, pawn, color) for i in range(len(self.board)) for pawn in pawns}
                        moves -= {(x,j, pawn, color) for j in range(len(self.board)) for pawn in pawns}
                        section_idxs = self._get_section_idxs(self._get_section_idx(x,y))
                        moves -= {(i,j,pawn, color) for i,j in section_idxs for pawn in pawns}
        return moves

    def _check_move_is_valid(self, x: int, y: int, pawn: Pawns, player: Colors):
        if x < 0 or y < 0 or x >= len(self.board) or y >= len(self.board[0]):
            raise InvalidMoveError(
                "x and y must be between 0 and " + str(NB_CELLS * NB_CELLS)
            )
        if self.board[x][y]:
            raise InvalidMoveError("already a pawn there")

        opponent_color = [c for c in Colors if c != player][0]
        if (pawn, opponent_color) in self._rows[x]:
            raise InvalidMoveError("there is an opponent's pawn in that row")
        if (pawn, opponent_color) in self._columns[y]:
            raise InvalidMoveError("there is an opponent's pawn in that column")
        
        section_idx = self._get_section_idx(x,y)
        if (pawn, opponent_color) in self._sections[section_idx]:
            raise InvalidMoveError("there is an opponent's pawn in that section")
        
    def _move_is_a_win(self, x: int, y: int):
        return self._row_win(x) or self._column_win(y) or self._section_win(x, y)

    def _ctxt(self, txt: str, color: Colors = None) -> str:
        if color:
            txt = color.value + txt + "\033[0m"
        return txt

    def _row_win(self, x: int):
        return len(self._rows[x]) == len(Pawns)

    def _column_win(self, y: int):
        return len(self._columns[y]) == len(Pawns)

    def _section_win(self, x: int, y: int):
        section_idx = self._get_section_idx(x,y)
        return len(self._sections[section_idx]) == len(Pawns)

    def _get_section_idx(self, x: int, y:int) -> int:
        section_idx = 0
        if x < 2 and y > 1:
            section_idx = 2
        if x > 1 and y < 2:
            section_idx = 1
        if x > 1 and y > 1:
            section_idx = 3
        return section_idx

    def _get_section_idxs(self, section_idx: int) -> int:
        if section_idx == 0:
            return [(0,0),(0,1), (1,0), (1,1)]
        if section_idx == 1:
            return [(0,2),(0,3), (1,2), (1,3)]
        if section_idx == 2:
            return [(2,0),(2,1), (3,0), (3,1)]
        if section_idx == 3:
            return [(2,2),(2,3), (3,2), (3,3)]

    def _add_to_optimized(self, x: int, y: int, pawn: Pawns, color: Colors):
        self._rows[x].add((pawn, color))
        self._columns[y].add((pawn, color))
        section_idx = self._get_section_idx(x,y)
        self._sections[section_idx].add((pawn, color))
