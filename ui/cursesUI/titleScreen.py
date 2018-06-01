import curses

from ui.cursesUI.levelScreen import LevelScreen
from .colors import COLORS
from itertools import cycle
import utils

class TitleScreen(object):

    THANKS = "            With special thanks to:" \
    "    MagmaFortress, for creating the game" \
    "    Bob Nystrom, for publishing \"Game Programming Patterns\"" \
    "    Juniper, for being a loving wife and tolerating my technobabble."

    def get_color(self, i):
        if 0 < i < 6:     return COLORS['GREEN'] | curses.A_BOLD
        elif 6 < i < 8:   return COLORS['BLUE']  | curses.A_BOLD
        elif 8 < i < 15:  return COLORS['CYAN']  | curses.A_BOLD
        elif 15 < i < 17: return COLORS['RED']   | curses.A_BOLD
        else:
            return 0


    def handle(self, key):
        if  not curses.ascii.isprint(key):
            return None

        if chr(key).upper() == 'Q':
            return lambda x: None
        elif chr(key).upper() == 'S':
            return LevelScreen(2)

    def __call__(self, stdscr):
        win = curses.newwin(28,58)
        win.border()
        stdscr.timeout(100)

        file_path = utils.data_file('TitleScreen.txt')
        with open(file_path, 'r') as f:
            for i, line in enumerate(f.readlines()):
                win.addstr(i+2, 1, line.rstrip(), self.get_color(i))

        # Scrolling thanks.
        thanks_iterator = cycle(range(0, len(self.THANKS)))

        for i in thanks_iterator:
            win.overwrite(stdscr)
            thanks = self.THANKS[i:] + self.THANKS[:i]
            stdscr.addstr(24, 1,thanks[:56])

            result = self.handle(stdscr.getch())
            if result:
                return result
