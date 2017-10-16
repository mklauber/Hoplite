import ast
import curses
import sys
import textwrap
import json

import engine
import shared
from ui.cursesUI.animations import Animation, Static as StaticAnimation
import units
import utils

import logging
logger = logging.getLogger(__name__)


def process(command, key):
    if key == curses.ascii.ESC:
        sys.exit(0)
    elif key == curses.KEY_BACKSPACE:
        return command[:-1]
    elif curses.ascii.isprint(key):
        return command + chr(key)
    else:
        return command

class LevelScreen(object):
    def __init__(self, level):
        self.events = []
        self.engine = engine.Engine(engine.load_level(level))

    def listener(self, state, action):
        """Listen for events the engine announces.  Attached to the engine in __call__"""

        # We simply append the events here so that we can decide if we want to process multiple ones later.
        self.events.append((state, action))

    def progress(self, screen):
        while len(self.events) > 0:
            state, action = self.events.pop(0)
            #logger.debug("Rendering %s", action)
            animation = Animation.create(action)
            animation.render(screen, state)

    def error_message(self, screen, error):
        logger.debug("Error Message")
        win = curses.newwin(21, 52)
        win.border()
        lines = textwrap.wrap(error.message, 50)
        for i, line in enumerate(lines, start=1):
            win.addstr(i, 1, line)
        win.overwrite(screen, 0, 0, 4, 3, 24, 55)
        while screen.getch() != curses.ascii.NL:
            pass

    def get_input(self, screen):
        key = screen.getch()
        command = ""
        while key != curses.ascii.NL:
            command = process(command, key)
            screen.addstr(1, 1, " " * 56)
            screen.addstr(1, 1, command[-56:])

            # Get the next input
            key = screen.getch()

        name, location = command.split(" ", 1)
        location = ast.literal_eval(location.strip())
        return shared.CreateAction({"type": name,
                                     "element": self.engine.state.actors[0],
                                     "target":location})

        raise utils.HopliteError("Input is not implemented for curses.UI yet")

    def __call__(self, screen, replay=True, *args, **kwargs):
        if replay == True:
            self.engine.listeners.add(self.listener)
            self.engine.fast_forward()
            self.progress(screen)
        else:
            self.engine.fast_forward()
            self.engine.listeners.add(self.listener)

        StaticAnimation().render(screen, self.engine.state)

        while len(set(u['team'] for u in self.engine.state.values())) > 1:
            StaticAnimation().render(screen, self.engine.state)
            try:
                self.engine.record()
            except units.RequiresInput:
                action = self.get_input(screen)
                self.engine.state.actors[0].set_next_action(action)
                continue
            except engine.InvalidMove as e:
                self.error_message(screen, e)
                continue

            # Render
            self.progress(screen)

        logger.debug("Game Complete")
        with open(utils.data_file("Last Game.json"), 'w') as f:
            f.write(json.dumps(self.engine.past, indent=2))
