import curses
import curses.ascii
import logging

logger = logging.getLogger(__name__)

from .colors import COLORS, UNITS
from ui.cursesUI.titleScreen import TitleScreen



def start():
    logging.basicConfig(level='DEBUG', filename='Hoplite.log')

    def main(stdscr):
        curses.curs_set(0)

        # Setup colors for later
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)


        COLORS.update({
            'GREEN': curses.color_pair(1),
            'RED': curses.color_pair(2),
            'BLUE': curses.color_pair(3),
            'CYAN': curses.color_pair(4),
            'MAGENTA': curses.color_pair(5)
        })

        UNITS.update({
            'Hero': ['H', COLORS['GREEN'] | curses.A_BOLD | curses.A_UNDERLINE],
            'Warrior': ['W', COLORS['RED'] | curses.A_BOLD | curses.A_UNDERLINE],
            'Archer': ['A', COLORS['BLUE'] | curses.A_BOLD | curses.A_UNDERLINE],
            'Demolitionist': ['D', COLORS['CYAN'] | curses.A_BOLD | curses.A_UNDERLINE],
            'Mage': ['M', COLORS['MAGENTA'] | curses.A_BOLD | curses.A_UNDERLINE]
        })

        # Manage game state
        current_screen = TitleScreen()
        while current_screen != None:
            current_screen = current_screen(stdscr)

    # Start the curses application
    curses.wrapper(main)


