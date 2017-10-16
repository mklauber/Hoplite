import grid
from shared import CreateAction

import logging
logger = logging.getLogger(__name__)


class Stab(object):
    @classmethod
    def get_action(cls, actor, state):
        for target in cls.threatened_cells(actor, state):
            if target in state and state[target]['team'] != actor['team']:
                return CreateAction({"type": "Stab", 
                                     "element": actor, 
                                     "target": target})

    @classmethod
    def targets(cls, actor, state):
        results = set()
        for target, element in state.items():
            if element['team'] != actor['team']:
                results |= grid.neighbors(target)
        return results

    @classmethod
    def threatened_cells(cls, actor, state):
        return grid.neighbors(state.find(actor))

class Move(object):

    @classmethod
    def get_action(cls, actor, state):
        try:
            path = grid.find_path(state, state.find(actor), actor.targets(state))
            return CreateAction({"type": "Move",
                                 "element": actor,
                                 "target": path[1]})
        except grid.NoPathExistsError:
            return None


class Slash(object):
    pass


class Lunge(object):
    pass


class Shoot(object):
    pass


class WizardsBeam(object):
    pass


class ThrowBomb(object):
    pass


class Explode(object):
    pass


class Jump(object):
    pass


class Burn(object):
    pass


class Prayer(object):
    pass


class Spear(object):
    pass
    

class DeepLunge(object):
    pass


class Bashable(object):
    pass

class Health(object):
    pass
