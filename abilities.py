import grid
from actions import CreateAction

import logging
logger = logging.getLogger(__name__)

class Stab(object):
    @classmethod
    def get_action(cls, actor, state):
        for target in cls.threatened_tiles(actor, state):
            if target in state and state[target]['team'] != actor['team']:
                return CreateAction({"type": "Stab", 
                                     "element": actor, 
                                     "target": target})
    
    @classmethod
    def threatened_tiles(cls, actor, state):
        location = state.find(actor)
        return grid.neighbors(location)
        
class Move(object):

    @classmethod
    def get_action(cls, actor, state):
        try:
            path = grid.find_path(state, state.find(actor), actor.threatened_tiles(state))
            return CreateAction({"type": "Move",
                                 "element": actor,
                                 "target": path[0]})
        except grid.NoPathExistsError:
            return None
        
    @classmethod
    def threatened_tiles(cls, actor, state):
        return set()


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
    @classmethod
    def threatened_tiles(cls, actor, state):
        return set()
