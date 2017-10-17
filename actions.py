import utils
import grid
from shared import CreateUnit

import logging
logger = logging.getLogger(__name__)


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

    def validate(self, state):
        raise NotImplementedError("Validate '%s' is not implemented", self.__class__.__name__)

class Spawn(Action):
    """Add a new element to the game grid"""

    def __init__(self, *args, **kwargs):
        super(Spawn, self).__init__(self, *args, **kwargs)
        self['element'] = CreateUnit(**kwargs['element'])

    def execute(self, state):
        state.actors.append(self.element)
        state[self.target] = self.element
    
    def rollback(self, state):
        state.actors.remove(self.element)
        del state[self.target]

    def validate(self, state):
        if self.target in state:
            return False
        return True

class ThrowBomb(Action):
    pass
    
class Move(Action):
    def execute(self, state):
        self.src = state.find(self.element)
        state[self.target] = state.pop(self.src)

    def rollback(self, state):
        state[self.src] = state.pop(self.target)
        
    def validate(self, state):
        if "Move" not in self.element["abilities"]:
            logger.debug("%s does not have the ability to Move")
            return False
        if self.target not in grid.neighbors(state.find(self.element)):
            return False
        if self.target in state:
            logger.debug("%s tried to move to %s, which is occupied by %s",
                         self.element, self.target, state[self.target])
            return False
        return True

class Attack(Action):
    damage = 1
    
    def execute(self, state):
        state[self.target]['health'] -= self.damage

    def rollback(self, state):
        state[self.target]['health'] += self.damage

class Stab(Attack):
    def validate(self, state):
        """Validate that the action doesn't violate any rules."""
        source = state.find(self.element)
        if self.target not in grid.neighbors(source):
            return False
        if "team" not in state.get(self.target, {}) or self.element['team'] == state[self.target]['team']:
            return False
        return True

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

class Bash(Action):
    def execute(self, state):
        self.vector = grid.unit_vector(state.find(self.element), self.target)
        logger.debug("Vector: %s", self.vector)
        logger.debug("element: %s", state.find(self.element))
        logger.debug("Target: %s", self.target)

        actor = state.pop(self.target, None)
        logger.debug("Actor: %s", actor)
        if actor != None:
            destination = grid.add(self.target, self.vector)
            logger.debug(destination)
            state[destination] = actor


    def rollback(self, state):
        actor = state.pop(grid.add(self.target, self.vector), None)
        if actor != None:
            state[self.target] = self.actor

    def validate(self, state):
        if self.target not in grid.neighbors(state.find(self.element)):
            return False

        if not grid.isValid(self.target):
            return False

        if self.target in state and 'Bashable' not in state[self.target]['abilities']:
            return False

        return True
