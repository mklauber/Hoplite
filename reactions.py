import abilities
import actions
import grid


def slash(action, state):
    if not isinstance(action, actions.Move) or abilities.Slash not in action['element'].abilities:
        return []
    
    actor = action['element']
    src  = state.find(actor)
    dest = action['target']
    targets = grid.neighbors(src) & grid.neighbors(dest)
    
    results = []
    for target in targets:
        if target in state and actor['team'] != state[target]['team']:
            results.append(actions.CreateAction({
                "type": "Slash",
                "element": actor,
                "target": target
            }))
            
    return results


def die(action, state):
    if not isinstance(action, actions.Attack):
        return []

    results = []
    element = state[action['target']]
    
    if "Health" in element.abilities and (element["health"] - action.damage) <= 0:
            results.append(actions.CreateAction({
                "type": "Die",
                "element": element,
                "target": action['target']
            }))
    return results


REACTIONS = [slash, die]
