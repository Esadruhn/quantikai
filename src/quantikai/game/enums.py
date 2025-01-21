from enum import Enum


class Pawns(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Colors(str, Enum):
    BLUE = "\033[44m"
    RED = "\033[41m"
