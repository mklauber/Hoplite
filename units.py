from collections import defaultdict
import json

import utils
import abilities
import engine

import logging
logger = logging.getLogger(__name__)

def initial_data():
    with open(utils.data_file("elements.json")) as f:
        return json.load(f)

class Unit(dict):
    initial_data = initial_data()
    counters = defaultdict(lambda: utils.Counter())

    @classmethod
    def create(cls, **kwargs):
        if kwargs.get('type', None) == "Hero":
            return Hero(**kwargs)
        else:
            return cls(**kwargs)

    def __init__(self, **kwargs):
        super(Unit, self).__init__(**kwargs)
        type = kwargs['type']
        initial_data = self.initial_data[type]

        self.update(initial_data)
        self.update(kwargs)
        if 'id' not in self:
            self['id'] = "%s-%s" % (type, self.counters[type].next())

    def __repr__(self):
        return "<" + self['id'] + ">"

    def __eq__(self, other):
        return self['id'] == other['id']

    @property
    def abilities(self):
        return [getattr(abilities, ability) for ability in self['abilities']]

    def get_action(self, state):
        for ability in self.abilities:
            action = ability.get_action(self, state)
            if action: 
                return action
        return None

    def threatened_cells(self, state):
        results = set()
        for ability in self.abilities:
            if hasattr(ability, "threatened_cells"):
                results |= ability.threatened_cells(self, state)
        return results

    def targets(self, state):
        results = set()
        for ability in self.abilities:
            if hasattr(ability, "targets"):
                results |= ability.targets(self, state)
        return results


class Hero(Unit):
    def __init__(self, **kwargs):
        super(Hero, self).__init__(**kwargs)
        self.next_action = None

    def set_next_action(self, action):
        self.next_action = action

    def get_action(self, state):
        if self.next_action == None:
            raise engine.RequiresInput("Actor %s requires input", self)
        else:
            action = self.next_action
            self.next_action = None
            return action
