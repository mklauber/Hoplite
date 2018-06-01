from collections import defaultdict
import json

import utils
import abilities


import logging
logger = logging.getLogger(__name__)

# Load the defaults for the various Game Elements from a file.
with open(utils.data_file("elements.json")) as f:
    INITIAL_DATA = json.load(f)


class RequiresInput(utils.HopliteError):
    """Error used to notify the UI that the current actor requires user input"""
    pass


class Unit(dict):
    """Class used for all Game Elements (With the exception of heroes, who subclass it).
       It's implemented following a Entity-Component Model."""

    # Create a counter for each type of game element.  Used to assign IDs.
    counters = defaultdict(lambda: utils.Counter())


    def __init__(self, **kwargs):
        super(Unit, self).__init__(**kwargs)
        type = kwargs['type']               # Grab type from kwargs, for cleanliness
        initial_data = INITIAL_DATA[type]   # Get the Unit's INITIAL_DATA

        self.update(initial_data)           # Set the initial data for the unit
        self.update(kwargs)                 # Override any data that was in different in the save.
        if 'id' not in self:                # Define an ID using the next number in the counter if not defined.
            self['id'] = "%s-%s" % (type, self.counters[type].next())

    def __repr__(self):
        """Represent the unit clearly in debug messages"""
        return "<" + self['id'] + ">"

    def __eq__(self, other):
        """Units are equal if their IDs are equal regardless of their other keys"""
        return self['id'] == other['id']

    @property
    def abilities(self):
        """Helper method to get the actual ability object for every unit's abilities"""
        return [getattr(abilities, ability) for ability in self['abilities']]

    def get_action(self, state):
        """For AI controlled actors, find an action by looking through each
           ability and seeing if it suggests and action at this time."""
        for ability in self.abilities:
            action = ability.get_action(self, state)
            if action: 
                return action
        return None

    def threatened_cells(self, state):
        """Helper method for determining all cells from which this Unit can attack opponents.
           This is particularly helpful for the Move action which uses this to find a cells to move towards."""
        results = set()
        for ability in self.abilities:
            if hasattr(ability, "threatened_cells"):
                results |= ability.threatened_cells(self, state)
        return results

    def targets(self, state):
        """Helper method for determining all cells this Unit can Attack at it's next turn."""
        results = set()
        for ability in self.abilities:
            if hasattr(ability, "targets"):
                results |= ability.targets(self, state)
        return results


class Hero(Unit):
    """A special case of a Unit, this unit requires user input to determine it's actions."""
    def __init__(self, **kwargs):
        super(Hero, self).__init__(**kwargs)
        self.next_action = None     # self.next_action is the sentinel to determine if the actor has it's next action.

    def set_next_action(self, action):
        """Set the next action"""
        self.next_action = action

    def get_action(self, state):
        """Override Unit.get_action to return the action set by the player.  If no action is set, raise an error."""
        if self.next_action == None:
            raise RequiresInput("Actor %s requires input", self)
        else:
            action = self.next_action
            self.next_action = None
            if action.validate(state) == False:  # Validate the action requested is valid, otherwise
                raise utils.InvalidMove("%s is not permitted" % action)  # raise an error to the user to respond to.
            return [action]
