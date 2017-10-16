from utils import HopliteError
import math

class InvalidPositionError(HopliteError):
    pass

def get_offset(pos):
    L, R = pos
    row = 4 + 2 * L + R
    col = 28 + R * 6
    return row, col

def get_cell(row, col):
    if col % 6 == 1:
        raise InvalidPositionError()
    row, col = float(row), float(col)
    R = int(math.ceil((col - 30) / 6))
    L = int(math.ceil((row - 4 -R) / 2))
    return (L, R)
