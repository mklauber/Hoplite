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
        """Handle and events that have occurred since the last time we've updated the UI.
           Events are recorded by self.listener.  Here we animate them.  Separating this allows us to combine
           animations in the future if we desire."""
        while len(self.events) > 0:
            state, action = self.events.pop(0)      # Get the first event
            animation = Animation.create(action)    # Create an animation for it
            animation.render(screen, state)         # execute the animation.

    def error_message(self, screen, error):
        """Display an error message to the user."""
        win = curses.newwin(21, 52)                 # Create a new window to display the error message.
        win.border()                                # Add a border for appearances
        lines = textwrap.wrap(error.message, 50)    # Our error message may not fit in one line.  wrap it.

        for i, line in enumerate(lines, start=1):   # Add the lines of our error message to our window.
            win.addstr(i, 1, line)

        win.overwrite(screen, 0, 0, 4, 3, 24, 55)   # Display the message in the center of our display
        while screen.getch() != curses.ascii.NL:    # Then wait until the user hits enter to continue
            pass

    def get_input(self, screen):
        """Allow the user to enter a command for the current Actor."""
        key = screen.getch()
        command = ""
        while key != curses.ascii.NL:
            command = process(command, key)
            screen.addstr(1, 1, " " * 56)
            screen.addstr(1, 1, command[-56:])

            # Get the next input
            key = screen.getch()

        try:
            name, location = command.split(" ", 1)
            location = ast.literal_eval(location.strip())
            return shared.CreateAction({"type": name,
                                         "element": self.engine.state.actors[0],
                                         "target":location})
        except:
            self.error_message("Unable to parse that command.")
            return None

        raise utils.HopliteError("Input is not implemented for curses.UI yet")

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
        finally:
            with open(utils.data_file("autosave.json"), 'w') as f:
                f.write(json.dumps(self.engine.past, indent=2))
