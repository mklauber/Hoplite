import utils
import json

class InvalidAction(utils.HopliteError):
    pass

def CreateAction(action):
    """Function used to create a Action object from a json dictionary"""
    # Import this here to avoid cyclical dependencies....
    # TODO: Fix these dependencies.
    from actions import Action

    for klass in utils.all_subclasses(Action):
        if action['type'] == klass.__name__:
            action['target'] = tuple(action['target'])
            return klass(**action)
    raise InvalidAction("%s is not a valid move." % json.dumps(action, indent=2))


def CreateUnit(**kwargs):
    """Function used to create a Unit object from a json dictionary"""
    # Import this here to avoid cyclical dependencies....
    # TODO: Fix these dependencies.
    from units import Hero, Unit

    # Special case for Heroes, who need to use a subclass that doesn't check abilities for actions
    if kwargs.get('type', None) == "Hero":
        return Hero(**kwargs)
    else:
        return Unit(**kwargs)
