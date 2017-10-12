import utils
import abilities

import logging
logger = logging.getLogger(__name__)

def CreateUnit(data):
    for klass in utils.all_subclasses(Unit):
        if data['type'] == klass.__name__:
            return klass(**data)


class Unit(dict):
    def __init__(self, *args, **kwargs):
        super(Unit, self).__init__(*args, **kwargs)
        if not 'id' in self:
            self['id'] = "%s-%s" % (self.__class__.__name__, self.counter.next())
        self['type'] = self.__class__.__name__

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
            results |= ability.threatened_cells(self, state) 
        return results

class Lava(Unit):
    counter = utils.Counter()
    abilities = ["Burn"]


class Warrior(Unit):
    counter = utils.Counter()
    abilties = ["Stab", "Move", "Health"]
    

class Archer(Unit):
    counter = utils.Counter()
    abilities = ["Shoot", "Move", "Bashable"]    
    

class Mage(Unit):
    counter = utils.Counter()
    abilities = ["WizardsBeam", "Move", "Bashable"]


class Demo(Unit):
    counter = utils.Counter()
    abilties = ["ThrowBomb", "Move", "Bashable"]


class Temple(Unit):
    counter = utils.Counter()
    abilities = ["Prayer"]


class Bomb(Unit):
    counter = utils.Counter()
    abilities = ["Explode", "Bashable"]
    
class Hero(Unit):
    counter = utils.Counter()
    def __init__(self, *args, **kwargs):
        super(Hero, self).__init__(*args, **kwargs)
        self['abilities'] = ["Stab", "Move", "Health"]
