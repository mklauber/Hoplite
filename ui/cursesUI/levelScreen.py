import curses
from .colors import COLORS
from .animations import Animation, Static as StaticAnimation
import engine
import time

import utils

import logging
logger = logging.getLogger(__name__)

class LevelScreen(object):
    def __init__(self, level):
        self.events = []
        self.engine = engine.Engine(engine.load_level(level))

    def listener(self, state, action):
        self.events.append((state, action))

    def __call__(self, screen, replay=True, *args, **kwargs):
        logger.debug(screen)
        if replay == True:
            self.engine.listeners.add(self.listener)
            self.engine.fast_forward()
            while len(self.events) > 0:
                state, action = self.events.pop(0)
                logger.debug("Rendering %s", action)
                animation = Animation.create(action)
                animation.render(screen, state)
        else:
            self.engine.fast_forward()
            self.engine.listeners.add(self.listener)

        StaticAnimation().render(screen, state)

        while len(set(u['team'] for u in self.engine.state.values())) > 1:
            self.engine.record()

            while len(self.events) > 0:
                state, action = self.events.pop(0)
                logger.debug("Rendering %s", action)
                animation = Animation.create(action)
                animation.render(screen, state)




