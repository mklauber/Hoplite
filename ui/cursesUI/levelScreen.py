import curses
from .colors import COLORS
from .animations import Animation, Static as StaticAnimation
import engine
import time

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

    def errorMessage(self, error):
        raise utils.HopliteError("Error Messages are not implemented for curses.UI yet")

    def get_input(self):
        pass

    def __call__(self, screen, replay=True, *args, **kwargs):
        logger.debug(screen)
        if replay == True:
            self.engine.listeners.add(self.listener)
            self.engine.fast_forward()
            self.progress(screen)
        else:
            self.engine.fast_forward()
            self.engine.listeners.add(self.listener)

        StaticAnimation().render(screen, self.engine.state)

        while len(set(u['team'] for u in self.engine.state.values())) > 1:
            # try:
            self.engine.record()
            # except engine.RequiresInput:
            #     self.get_input()
            #     continue
            # except engine.InvalidInput as e:
            #     self.error_message(e)
            #     continue
            self.progress(screen)
