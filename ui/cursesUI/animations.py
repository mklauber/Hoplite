from abc import ABCMeta, abstractmethod
import curses
from math import copysign, floor

from ui.cursesUI import COLORS, UNITS
from ui.cursesUI.offset import get_offset
import utils

import logging
logger = logging.getLogger(__name__)

def get_background():
    background = curses.newwin(27, 58)
    background.border()

    with open(utils.data_file('background.txt')) as f:
        for i, row in enumerate(f.readlines(), start=1):
            background.addstr(i, 1, row[:-1], curses.A_DIM)

    return background


def render_unit(position, unit, win):
    row, col = get_offset(position)

    if unit['type'] == 'Hero':
        win.addstr(row, col, *UNITS['Hero'])
    elif unit['type'] == 'Warrior':
        win.addstr(row, col, *UNITS['Warrior'])
    elif unit['type'] == 'Archer':
        win.addstr(row, col, *UNITS['Archer'])
    elif unit['type'] == 'Demolitionist':
        win.addstr(row, col, *UNITS['Demolitionist'])
    elif unit['type'] == 'Mage':
        win.addstr(row, col, *UNITS['Mage'])


def render(state):
    win = curses.newwin(27, 58)

    for position, item in state.items():
        render_unit(position, item, win)
    return win


def text_path(src, dest):
    """Given two cells, figure out the path for a given object to pass between them."""
    sRow, sCol = get_offset(src)
    tRow, tCol = get_offset(dest)

    row_diff = tRow - sRow
    col_diff = tCol - sCol
    distance = max(row_diff, col_diff, key=lambda x: abs(x))

    for i in range(0, distance, int(copysign(1, distance))):
        if abs(row_diff) >= abs(col_diff):
            slope = float(col_diff) / float(row_diff) if col_diff != 0 else 0
            yield sRow + i, sCol + int(floor(i * slope))
        else:
            slope = float(row_diff) / float(col_diff) if col_diff != 0 else 0
            yield sRow + int(floor(i * slope)), sCol + i

class Animation(object):
    __metaclass__ = ABCMeta

    @classmethod
    def create(cls, action):
        for klass in utils.all_subclasses(cls):
            if action.get('type', None) == klass.__name__:
                logger.info("Creating %s Animation", klass.__name__)
                return klass(action)
        return Static(action)

    @abstractmethod
    def render(self):
        pass


class Static(Animation):
    def __init__(self, action=None):
        pass

    def render(self, stdscr, state):
        stdscr.timeout(100)
        get_background().overwrite(stdscr)
        render(state).overlay(stdscr)
        stdscr.getch()


class Die(Animation):
    def __init__(self, action):
        pass

    def render(self, screen, state):
        pass


class Stab(Animation):
    def __init__(self, action):
        self.action = action
        self.target = action['target']
        self.element = action['element']

    def render(self, stdscr, state):
        background = get_background()
        elements = render(state)
        self.source = state.find(self.element)

        sRow, sCol = get_offset(self.source)
        tRow, tCol = get_offset(self.target)
        type = self.action["element"]["type"]

        stdscr.timeout(150)
        for row, col in text_path(self.source, self.target):
            background.overwrite(stdscr)
            elements.overlay(stdscr)
            stdscr.addstr(sRow, sCol, "_", curses.A_DIM)
            stdscr.addstr(row, col, *UNITS[type])
            stdscr.getch()


        for row, col in text_path(self.target, self.source):
            background.overwrite(stdscr)
            elements.overlay(stdscr)
            stdscr.addstr(sRow, sCol, "_", curses.A_DIM)
            stdscr.addstr(tRow, tCol, "_", curses.A_DIM)
            stdscr.addstr(row, col, *UNITS[type])
            stdscr.getch()
