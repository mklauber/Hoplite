import actions
from shared import CreateAction
import grid

import logging
logger = logging.getLogger(__name__)


def slash(action, state):
    """The Slash action is triggered if a character able to slash steps past an enemy"""

    # Check to make sure the actor is Moving and that they can slash
    if not isinstance(action, actions.Move) or "Slash" not in action['element']['abilities']:
        return []
    
    actor   = action['element']
    src     = state.find(actor)
    dest    = action['target']
    # Can only target cells that were next to the actor at the start and end of his movement.
    # By doing it this way, we can handle leaping with the same test.
    targets = grid.neighbors(src) & grid.neighbors(dest)
    
    results = []
    for target in targets:
        # for every cell in targets, check if an enemy is present
        if target in state and actor['team'] != state[target]['team'] and "Health" in state[target]['abilities']:
            # If so, add a Slash Action as a reaction.
            reaction = CreateAction({
                "type": "Slash",
                "element": actor,
                "target": target
            })
            logger.debug("%s triggered %s", action, reaction)
            results.append(reaction)
            
    return results


def lunge(action, state):
    """The Slash action is triggered if a character able to slash steps past an enemy"""

    # Check to make sure the actor is Moving and that they can slash
    if not isinstance(action, actions.Move) or "Lunge" not in action['element']['abilities']:
        return []

    actor   = action['element']
    src     = state.find(actor)
    dest    = action['target']

    # confirm this is a move in a direction we can lunge.
    vector = grid.unit_vector(src, dest)
    if vector not in grid.DIRECTIONS:
        return []

    # Determine the target
    target = grid.add(dest, vector)
    if target in state and actor['team'] != state[target]['team']  and "Health" in state[target]['abilities']:
        # If so, add a Slash Action as a reaction.
        reaction = CreateAction({
            "type": "Lunge",
            "element": actor,
            "target": target
        })
        logger.debug("%s triggered %s", action, reaction)
        return [reaction]
    return []


def die(action, state):
    """Dying is a reaction to being attacked."""

    # We're using inheritance here to make checking if we were attacked simpler.
    if not isinstance(action, actions.Attack):
        return []

    element = state[action.target]

    # Make sure the attack brings our health below 0
    if "Health" in element['abilities'] and (element["health"] - action.damage) <= 0:
        # If so, add a Die action as a reaction
        reaction = CreateAction({
            "type": "Die",
            "element": element,
            "target": action.target
        })
        logger.debug("%s triggered %s", action, reaction)
        return [reaction]
    return []


# Expose these as an list.
REACTIONS = [slash, lunge, die]
