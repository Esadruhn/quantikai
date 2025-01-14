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
    pawns: list[Pawns] = field(default_factory=lambda:NB_CELLS*[pawn for pawn in Pawns])

    def remove(self, pawn: Pawns):
        self.check_has_pawn(pawn)
        self.pawns.remove(pawn)

    def check_has_pawn(self, pawn):
        if not pawn in self.pawns:
            raise InvalidMoveError("You do not have this pawn.")

    def print_pawns(self):
        t = ""
        for pawn in self.pawns:
            t += pawn.value + " "
        print("Player " + self.color.name + " available pawns: " + t)

@dataclass
class Board:
    board: list[list[tuple[Pawns, Colors]]] = field(default_factory=lambda: [[None for _ in range(4)] for _ in range(4)])

    def play(self, x: int, y: int, pawn: Pawns, color: Colors):
        pawn = Pawns(pawn)
        color = Colors(color)
        self._check_move_is_valid(x, y, pawn, color)
        self.board[x][y] = (pawn, color)
        return self._move_is_a_win(x,y)
    
    def print(self):
        upper_separator = " ____ "*NB_CELLS + "  " + "____  "*NB_CELLS +"\n"
        str_board = upper_separator
        for i in range(NB_CELLS*2):
            for j in range(NB_CELLS*2):
                if self.board[i][j]: 
                    str_board += self._ctxt("|__" + self.board[i][j][0].value + "_|", self.board[i][j][1])
                else:
                    str_board += "|____|"
                if j+1 == NB_CELLS: str_board += " "
            str_board += "\n"
            if i+1 == NB_CELLS: str_board += upper_separator
            
        print(str_board)

    def _check_move_is_valid(self, x: int, y: int, pawn: Pawns, player: Colors):
        if x < 0 or y < 0 or x >= len(self.board) or y >= len(self.board[0]):
            raise InvalidMoveError("x and y must be between 0 and " + str(NB_CELLS*NB_CELLS))
        if self.board[x][y]:
            raise InvalidMoveError("already a pawn there")
        for element in self.board[x]:
            if element and element[0] == pawn and element[1] != player:
                raise InvalidMoveError("there is an opponent's pawn in that row")
        for row in self.board:
            if row[y] and row[y][0] == pawn and row[y][1] != player:
                raise InvalidMoveError("there is an opponent's pawn in that column")
        # check section
        for row in self.board[x  // NB_CELLS: x  // NB_CELLS + NB_CELLS]:
            for element in row[y  // NB_CELLS: y  // NB_CELLS + NB_CELLS]:
                if element and element[0] == pawn and element[1] != player:
                    raise InvalidMoveError("there is an opponent's pawn in that section")
                
    def _move_is_a_win(self, x: int, y: int):
        return self._row_win(x) or self._column_win(y) or self._section_win(x,y)

    def _ctxt(self, txt: str, color: Colors=None) -> str:
        if color: txt = color.value + txt + "\033[0m"
        return txt

    def _row_win(self, x: int):
        others = list()
        for element in self.board[x]:
            if not element or element[0] in others:
                return False
            others.append(element[0])
        return True

    def _column_win(self, y:int):
        others = list()
        for row in self.board:
            if not row[y] or row[y][0] in others:
                return False
            others.append(row[y][0])
        return True

    def _section_win(self, x: int, y: int):
        others = list()
        for row in self.board[x  // NB_CELLS: x  // NB_CELLS + NB_CELLS]:
            for element in row[y  // NB_CELLS: y  // NB_CELLS + NB_CELLS]:
                if not element or element[0] in others:
                    return False
                others.append(element[0])
        return True

    def have_possible_move(self, color: Colors):
        # TODO: test
        for x, row in enumerate(self.board):
            for y, _ in enumerate(row):
                for pawn in Pawns:
                    try:
                        self._check_move_is_valid(x, y, pawn, color)
                        return True
                    except InvalidMoveError:
                        pass
        return False
