from ui import cursesUI, pygameUI, terminalUI
import argparse
import sys

import logging
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--ui', help="Choose the output UI", type=str,
                    choices=['terminal', 'curses', 'pygame'], default="curses")
parser.add_argument('--test', type=str, choices=['engine'])



if __name__ == '__main__':
    logging.basicConfig(filename="Hoplite.log",
                        format="%(module)s:%(lineno)d %(levelname)s %(message)s",
                        level="DEBUG")
    results = parser.parse_args(sys.argv[1:])
    if results.ui == 'curses':
        cursesUI()
    elif results.test == "engine":
        import engine
        engine.test()
