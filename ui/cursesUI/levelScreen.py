import curses
import textwrap

import engine
from ui.cursesUI.animations import Animation, Static as StaticAnimation
import utils

import logging
logger = logging.getLogger(__name__)

def parseInput(string):
    pass

class LevelScreen(object):
    def __init__(self, level):
        self.events = []
        self.engine = engine.Engine(engine.load_level(level))

    def listener(self, state, action):
        self.events.append((state, action))

    def progress(self, screen):
        while len(self.events) > 0:
            state, action = self.events.pop(0)
            logger.debug("Rendering %s", action)
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

    def get_input(self):
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
            try:
                self.engine.record()
            except engine.RequiresInput:
                self.get_input()
                continue
            except engine.InvalidMove as e:
                self.error_message(screen, e)
                continue
            except Exception:
                raise

            # Render
            self.progress(screen)
