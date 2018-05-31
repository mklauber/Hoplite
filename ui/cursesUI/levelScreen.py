# -*- coding: utf-8 -*-
import ast
import curses
import sys
import textwrap
import json

import engine
import shared
from ui.cursesUI import offset
from ui.cursesUI.animations import Animation, Static as StaticAnimation
from ui.cursesUI.colors import COLORS
import units
import utils

import logging
logger = logging.getLogger(__name__)


class QuitError(utils.HopliteError):
    pass

def process(command, key):
    if key == curses.KEY_BACKSPACE:
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
        """Handle and events that have occurred since the last time we've updated the UI.
           Events are recorded by self.listener.  Here we animate them.  Separating this allows us to combine
           animations in the future if we desire."""
        while len(self.events) > 0:
            state, action = self.events.pop(0)      # Get the first event
            animation = Animation.create(action)    # Create an animation for it
            animation.render(screen, state)         # execute the animation.

    def message(self, screen, message):
        """Display an error message to the user."""
        win = curses.newwin(21, 52)                 # Create a new window to display the error message.
        win.border()                                # Add a border for appearances
        lines = textwrap.wrap(message, 50)    # Our error message may not fit in one line.  wrap it.

        for i, line in enumerate(lines, start=1):   # Add the lines of our error message to our window.
            win.addstr(i, 1, line)

        win.overwrite(screen, 0, 0, 4, 3, 24, 55)   # Display the message in the center of our display
        while screen.getch() != curses.ascii.NL:    # Then wait until the user hits enter to continue
            pass

    def highlight_char(self, screen):
        """Wrapper function for everything required to highlight a given cell."""
        r, c = offset.get_offset(self.engine.state.find(self.engine.state.actors[0]))
        attrs = (screen.inch(r, c) & curses.A_ATTRIBUTES) | curses.A_REVERSE
        screen.chgat(r, c, 1, attrs)

    def draw_health(self, screen):
        """Draw the health of the current Hero.
           Should only be called on units that are waiting for player input"""
        screen.addstr(3,2, "Health: "+ u"♥".encode("utf-8") * self.engine.state.actors[0]['health'], COLORS['RED']| curses.A_BOLD)

    def get_input(self, screen):
        """Allow the user to enter a command for the current Actor."""
        key = screen.getch()
        command = ""
        while key != curses.ascii.NL:
            if key == curses.ascii.ESC:
                sys.exit(0)
            command = process(command, key)
            screen.addstr(1, 1, " " * 56)
            screen.addstr(1, 1, command[-56:])

            # Get the next input
            key = screen.getch()

        if command.lower() == "quit":
            raise QuitError

        try:
            name, location = command.split(" ", 1)
            location = ast.literal_eval(location.strip())
            return shared.CreateAction({"type": name,
                                         "element": self.engine.state.actors[0],
                                         "target":location})
        except shared.InvalidAction as e:
            logger.warn("Unable to parse: %s" % e.message)
            self.message(screen, "Unable to parse that command.")
            return None

    def __call__(self, screen, replay=True, *args, **kwargs):
        try:
            if replay == True:
                self.engine.listeners.add(self.listener)
                self.engine.fast_forward()
                self.progress(screen)
            else:
                self.engine.fast_forward()
                self.engine.listeners.add(self.listener)

            StaticAnimation().render(screen, self.engine.state)

            while self.engine.complete == False:
                StaticAnimation().render(screen, self.engine.state)
                try:
                    self.engine.record()
                except units.RequiresInput:
                    self.draw_health(screen)
                    self.highlight_char(screen)
                    action = self.get_input(screen)
                    self.engine.state.actors[0].set_next_action(action)
                    continue
                except engine.InvalidMove as e:
                    self.message(screen, e.message)
                    continue

                # Render
                self.progress(screen)

        except QuitError:
            with open(utils.data_file("autosave.json"), 'w') as f:
                f.write(json.dumps(self.engine.past, indent=2))
            from ui.cursesUI.titleScreen import TitleScreen
            return TitleScreen()
        except:
            with open(utils.data_file("autosave.json"), 'w') as f:
                f.write(json.dumps(self.engine.past, indent=2))
                raise

        if self.engine.state.actors[0]['team'] == 'red':
            self.message(screen, "Congrats, you've beaten the level")
            return LevelScreen('level1.json')
        else:
            self.message(screen, "I'm sorry, you've died.")
            from ui.cursesUI.titleScreen import TitleScreen
            return TitleScreen()

        logger.debug("Game Complete")


