import shared
from reactions import REACTIONS
from shared import CreateAction
import copy
import json
import utils
import grid
import random


import logging
logger = logging.getLogger(__name__)


class State(dict):
    """This State object manages the current game state.  This involves the location of every item on the map, and
       the order in which elements take their turns."""

    def __init__(self):
        self.actors = []    # Track the actors in a list.  We'll treat this a a queue for the purposes of turn order.

    def __setitem__(self, key, value):
        """Tweak this to make sure every key is a tuple of two ints."""
        key = (int(key[0]), int(key[1]))
        super(State, self).__setitem__(key, value)

    def find(self, target):
        """function to look up the location of an item in the state."""
        for key, value in self.items():
            if value == target:
                return key
        raise KeyError()

    def __str__(self):
        """Make printing the state nicer."""
        return "Actors: %s\nGrid: %s" % (self.actors, super(State, self).__str__())


class Engine(object):
    """An engine object manages the progression of the game.  It tracks turns and turn order, and determines reactions
       to actions taken."""

    def __init__(self, history):
        """Every engine has to have a starting state, which for simplicity is a history to replay."""
        self.past = []          # All the previous turns
        self.future = history   # All actions recorded but not played back against the stte
        self.state = State()    # The current state of the game
        self.listeners = set()  # listeners are functions that want to know about actions during the play of the game.

    @property
    def complete(self):
        """Make knowing if the game is over simple
           The game is over when one team remains."""
        return len(self.remaining_teams) == 1

    @property
    def remaining_teams(self):
        """Returns a list of teams remaining on the battlefield"""
        return set(element['team'] for element in self.state.values() if 'team' in element)

    @property
    def current_actor(self):
        return self.state.actors[0]

    def fast_forward(self):
        """Execute any remaining future items"""
        while self.future != []:
            self.step_forward()

    def rewind(self):
        """Rewind all past turns"""
        while self.past != []:
            self.step_backward()

    def step_backward(self):
        """Reverse one turn from the past against the current state"""

        if len(self.past) == 0:  # There are no previous turns, so don't do anything.
            return

        turn = self.past.pop()                  # Get the previous turn
        if len(self.state.actors) > 0:          # If there's more than one actor make
            actor = self.state.actors.pop()     # sure to keep track of turn order.
            self.state.actors.insert(0, actor)  #

        for action in reversed(turn):   # For every action (and reaction) in the turn
            action.rollback(self.state)  # Undo them in reverse order

        self.future.insert(0, turn)  # Add this turn to the future in case we want to redo it.

    def step_forward(self):
        """Playback one turn from the future against the current state"""

        if len(self.future) == 0:  # There are no future turns, so don't do anything.
            return

        turn = self.future.pop(0)               # Get the next turn
        if len(self.state.actors) > 0:          # If there's more than one actor make
            actor = self.state.actors.pop(0)    # sure to keep track of turn order.
            self.state.actors.append(actor)     #

        for action in turn:                 # For every action (and reaction) in the turn
            self.emit(self.state, action)   # Announce them, and the current state.
            action.execute(self.state)      # execute the action against the current state

        self.past.append(turn)  # Add this turn to the past in case we want to undo it.

    def emit(self, state, action):
        """Announce to any interested listeners each action and the state before the action"""
        state = copy.deepcopy(state)    # Copy the state so that progressing the game doesn't screw up event listeners
        for listener in self.listeners:  # who delay parsing the (state, action) messages.
            listener(state, action)

    def record(self, overwrite=False):
        """Record new actions for the game"""

        if overwrite == False and self.future != []:  # Sometimes we may not want to be able to record new actions.
            raise utils.HopliteError("Cannot record a turn when future turns exist unless the overwrite flag is True")

        actor = self.state.actors[0]            # Get the current actor, and ask them for their action, given the state
        # Heroes may raise a NeedsInput Exception here for the UI to respond to.
        actions = actor.get_action(self.state)

        # Copy the state, because determining reactions requires us to modify the current state (in case a reaction
        # causes a future reaction).  So we copy the state, and then apply them to our main state later.
        state = copy.deepcopy(self.state)

        turn = []
        while len(actions) != 0:  # While we have an action left in the turn
            action = actions.pop(0)
            logger.debug(action)
            reactions = determine_reactions(action, state)  # Determine the reaction that action triggers
            actions = reactions + actions   # Insert them immediately after the action that triggers them.
            action.execute(state)      # Modify the current state by executing the action
            turn.append(action)             # Add it to the turn.

        # Once we've generated the full turn, add it to the future, and then just fast forward, so we can reuse our
        # code for applying and announcing actions.
        self.future.append(turn)
        self.fast_forward()


def determine_reactions(action, state):
    """For our game, certain actions can cause reactions that should happen during the same turn.
       For example, Moving past an enemy may trigger a slash Action."""

    reactions = []              # make a list of all reactions triggered by the action,
    for behavior in REACTIONS:  # by iterating through the reactions and asking them
        reactions.extend(behavior(action, state))
    return reactions


def load_level(filename):
    """Load a level from a history file."""
    result = []
    with open(utils.data_file(filename), 'r') as f:
        level = json.loads(f.read())
    for turn in level:
        computed = []
        for action in turn:
            computed.append(CreateAction(action))  # Turn every action into an action object, not just a dict
        result.append(computed)
    return result


def generate_level(number):
    with open(utils.data_file('levels.json'), 'r') as f:
        data = json.load(f)
        level = data[str(number)]

    results = []
    remaining_cells = copy.copy(grid.VALID_CELLS)

    # Add a hero
    results.append(CreateAction({
        "type": "Spawn",
        "target": [10, 0],
        "element": {
                "type": "Hero",
                "team": "red"
        }
    }))
    remaining_cells.remove((10, 0))

    # Add the enemies
    for kind, count in level.items():
        for i in range(0, count):
            location = random.choice(remaining_cells)
            results.append(CreateAction({
                "type": "Spawn",
                "target": location,
                "element": {
                    "type": kind,
                    "team": "blue"
                }
            }))
            remaining_cells.remove(location)
    logger.info(results)

    return [results]
