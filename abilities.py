import grid
from shared import CreateAction
from copy import copy

import logging
logger = logging.getLogger(__name__)


class Stab(object):
    @classmethod
    def get_action(cls, actor, state):
        for target in cls.threatened_cells(actor, state):
            if target in state and 'health' in state[target] and state[target]['team'] != actor['team']:
                return [CreateAction({"type": "Stab",
                                      "element": actor,
                                      "target": target})]

    @classmethod
    def targets(cls, actor, state):
        results = set()
        for target, element in state.items():
            if 'team' not in element or element['team'] != actor['team']:
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
            if len(path) > 1:
                return [CreateAction({"type": "Move",
                                      "element": actor,
                                      "target": path[1]})]
            return [CreateAction({"type": "Null",
                                  "element": actor,
                                  "target": state.find(actor)})]

        except grid.NoPathExistsError:
            return None


class Slash(object):
    pass


class Lunge(object):
    pass


class Shoot(object):
    @classmethod
    def get_action(cls, actor, state):
        src = state.find(actor)

        blocked = [d for d in grid.DIRECTIONS if grid.add(src, d) in state]

        for i in range(2, 5):
            for direction in grid.DIRECTIONS:
                if direction in blocked:    # Don't check cells that have something in the way.
                    continue
                target = grid.add(src, grid.mult(direction, i))
                if target in state and 'health' in state[target] and state[target]['team'] != actor['team']:
                    return [CreateAction({"type": "Shoot",
                                          "element": actor,
                                          "target": target})]
                elif target in state:
                    blocked.append(direction)

    @classmethod
    def targets(cls, actor, state):
        results = set()
        for target, element in state.items():
            if 'team' not in element or element['team'] == actor['team']:
                continue

            directions = copy(grid.DIRECTIONS)
            blocked = []
            for i in range(1, 5):
                for d in directions:
                    cell = grid.add(target, grid.mult(d, i))
                    if d in blocked:
                        continue
                    elif cell in state.keys() and cell != state.find(actor):
                        blocked.append(d)
                    else:
                        results.add(cell)

            results -= grid.lines(target, 1)
        return results

    @classmethod
    def threatened_cells(cls, actor, state):
        src = state.find(actor)
        return grid.lines(src, 5) - grid.lines(src, 1)


class WizardsBeam(object):
    @classmethod
    def get_action(cls, actor, state):
        src = state.find(actor)
        actor['beam cooldown'] -= 1
        if actor['beam cooldown'] >= 0:  # Only fire every other turn
            return

        for direction in grid.DIRECTIONS:
            cells = grid.line(src, direction, 5)
            cells.remove(src)
            logger.debug("Cells: %s", cells)
            elements = [state.get(cell) for cell in cells if cell in state]
            logger.debug("%s sees %s in direction %s", actor, elements, direction)
            teams = [e['team'] for e in elements if 'team' in e]
            if actor['team'] in teams:  # Can't shoot Allies
                logger.debug("%s can't shoot %s or he'll hit an ally", actor, direction)
                continue
            elif len(teams) == 0:   # Don't shoot at nothing.
                logger.debug("%s can't shoot %s or he'll miss", actor, direction)
                continue
            else:
                return [CreateAction({"type": "WizardsBeam",
                                      "element": actor,
                                      "target": t}) for t in cells]

    @classmethod
    def targets(cls, actor, state):
        results = set()
        results.add(state.find(actor))
        return results


class ThrowBomb(object):
    @classmethod
    def get_action(cls, actor, state):
        actor['bomb cooldown'] -= 1
        if actor['bomb cooldown'] >= 0:
            return

        for cell in grid.burst(state.find(actor), 3):
            if cell in state.keys():
                continue

            # Check who we're targeting
            neighbors = [state[c] for c in grid.neighbors(cell) if c in state]
            teams = set(n['team'] for n in neighbors if 'team' in n)
            if actor['team'] in teams:  # Can't hit allies.
                continue
            elif len(teams) == 0:   # Don't target cells where you won't hit anyone.
                continue
            else:
                return [CreateAction({
                    'type': "ThrowBomb",
                    'element': actor,
                    'target': cell
                })]

    @classmethod
    def targets(cls, actor, state):
        targets = set()
        avoid = set()
        for cell, element in state.items():
            if 'team' not in element or actor['team'] != element['team']:
                targets |= grid.burst(cell, 3) - grid.burst(cell, 2)
                avoid |= grid.burst(cell, 1)
        return targets - avoid


class Explode(object):
    @classmethod
    def get_action(cls, actor, state):
        results = []
        results.append(CreateAction({
            'type': "Explode",
            'element': actor,
            'target': state.find(actor)
        }))
        for cell in grid.neighbors(state.find(actor)):
            results.append(CreateAction({
                'type': "BlastWave",
                'element': actor,
                'target': cell
            }))
        return results


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
