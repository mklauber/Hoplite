import utils
from units import CreateUnit

def CreateAction(action):
    for klass in utils.all_subclasses(Action):
        if action['type'] == klass.__name__:
            return klass(**action)


class Action(dict):
    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        self['type'] = self.__class__.__name__

    @property
    def element(self):
        return self['element']

    @property
    def target(self):
        return self['target']

    def __repr__(self):
        return "<%s %s %s>" % (self.__class__.__name__, self['element'], self['target'])

    def execute(self, state):
        raise NotImplementedError("Execute '%s' is not implemented" % self.__class__.__name__)

    def rollback(self, state):
        raise NotImplementedError("Rollback '%s' is not implemented" % self.__class__.__name__)

class Spawn(Action):
    def __init__(self, *args, **kwargs):
        super(Spawn, self).__init__(self, *args, **kwargs)
        self['element'] = CreateUnit(kwargs['element'])

    def execute(self, state):
        state.actors.append(self.element)
        state[self.target] = self.element
    
    def rollback(self, state):
        state.actors.remove(self.element)
        del state[self.target]

class ThrowBomb(Action):
    pass
    
class Move(Action):
    def execute(self, state):
        self.src = state.find(self.element)
        state[self.target] = state.pop(self.src)

    def rollback(self, state):
        state[self.src] = state.pop(self.target)
        

class Attack(Action):
    damage = 1
    
    def execute(self, state):
        state[self.target]['health'] -= self.damage

    def rollback(self, state):
        state[self.target]['health'] += self.damage

class Stab(Attack):
    pass

class Slash(Attack):
    pass

class Lunge(Attack):
    pass

class DeepLunge(Attack):
    pass

class Shoot(Attack):
    pass


class WizardsBeam(Attack):
    pass


class Explode(Attack):
    pass
    
    
class Die(Action):
    def execute(self, state):
        self.turn_position = state.actors.index(self.element)
        state.actors.remove(self.element)
        del state[self.target]

    def rollback(self, state):
        state.actors.insert(self.turn_position, self.element)
        state[self.target] = self.element
    
