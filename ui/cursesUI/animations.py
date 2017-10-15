from abc import ABCMeta, abstractmethod
import curses

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
