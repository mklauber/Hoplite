from abc import ABCMeta, abstractmethod
import curses
from math import copysign, floor
from copy import copy

from ui.cursesUI import COLORS, UNITS
from ui.cursesUI.offset import get_offset
import utils

import grid

import logging
logger = logging.getLogger(__name__)

ANIMATION_DURATION = 750


def get_background():
    background = curses.newwin(28, 58)
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
        data = copy(UNITS['Demolitionist'])
        data[0] = 'D*' if unit['bomb cooldown'] <= 0 else 'D'
        win.addstr(row, col, *data)
    elif unit['type'] == 'Bomb':
        win.addstr(row, col, *UNITS['Bomb'])
    elif unit['type'] == 'Mage':
        data = copy(UNITS['Mage'])
        data[0] = 'M*' if unit['beam cooldown'] <= 0 else 'M'
        win.addstr(row, col, *data)


def render(state):
    win = curses.newwin(28, 58)

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
    def __init__(self, action):
        self.action = action
        self.target = action['target']
        self.element = action['element']

    @classmethod
    def create(cls, action):
        for klass in utils.all_subclasses(cls):
            if action.get('type', None) == klass.__name__:
                logger.info("Creating %s Animation", klass.__name__)
                return klass(action)
        logger.info("Defaulting to StaticAnimation for %s", action)
        return Static(action)

    def render(self, stdscr, state):
        background = get_background()
        elements = render(state)

        timeout = min(75, ANIMATION_DURATION / len(list(self.frames(state))))

        stdscr.timeout(timeout)
        for frame in self.frames(state):
            background.overwrite(stdscr)
            elements.overlay(stdscr)
            frame(stdscr)
            stdscr.getch()


class Static(Animation):
    def __init__(self, action=None):
        pass

    def render(self, stdscr, state):
        stdscr.timeout(100)
        get_background().overwrite(stdscr)
        render(state).overlay(stdscr)
        stdscr.getch()


class Move(Animation):
    def frames(self, state):
        source = state.find(self.element)

        sRow, sCol = get_offset(source)
        type = self.action["element"]["type"]

        # Path to new square
        for row, col in text_path(source, self.target):
            def path_to_stab(screen):
                screen.addstr(sRow, sCol, "__", curses.A_DIM)
                screen.addstr(row, col, *UNITS[type])

            yield path_to_stab


class Jump(Move):
    pass


class ThrowBomb(Animation):
    def frames(self, state):
        source = state.find(self.element)

        sRow, sCol = get_offset(source)
        type = self.action["element"]["type"]

        # Path to new square
        for row, col in text_path(source, self.target):
            def path_to_stab(screen):
                screen.addstr(sRow, sCol+1, "_", curses.A_DIM)
                screen.addstr(row, col, *UNITS['Bomb'])

            yield path_to_stab


class Die(Animation):

    def render(self, screen, state):
        pass


class Stab(Animation):

    def frames(self, state):
        source = state.find(self.element)

        sRow, sCol = get_offset(source)
        tRow, tCol = get_offset(self.target)
        type = self.action["element"]["type"]

        # Path to Stab
        for row, col in text_path(source, self.target):
            def path_to_stab(screen):
                screen.addstr(sRow, sCol, "__", curses.A_DIM)
                screen.addstr(row, col, *UNITS[type])
            yield path_to_stab

        # Path from Stab
        for row, col in text_path(self.target, source):
            def path_from_stab(screen):
                screen.addstr(sRow, sCol, "__", curses.A_DIM)
                if state[self.target]['health'] - self.action.damage <= 0:
                    screen.addstr(tRow, tCol, "__", curses.A_DIM)
                screen.addstr(row, col, *UNITS[type])
            yield path_from_stab


class Slash(Stab):
    pass


class Lunge(Stab):
    pass


class Shoot(Animation):
    def frames(self, state):
        source = state.find(self.element)
        for row, col in text_path(source, self.target):
            def frame(screen):
                screen.addstr(row, col, '|', COLORS['BLUE'] | curses.A_BOLD)
            yield frame


class Explode(Animation):
    def frames(self, state):

        animation = ['/\\', '/  \\', '/\\/\\', '\\  /', '/\\/\\', '/\\']

        for frame in animation:
            def draw_flame(screen):
                sRow, sCol = get_offset(self.target)
                screen.addstr(sRow, sCol + 1 - len(frame)/2, frame, COLORS['FIRE'])
            yield draw_flame


class BlastWave(Explode):
    pass
