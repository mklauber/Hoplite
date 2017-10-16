import utils


def CreateAction(action):
    from actions import Action
    for klass in utils.all_subclasses(Action):
        if action['type'] == klass.__name__:
            return klass(**action)


def CreateUnit(**kwargs):
    """Function used to create a Unit object from a json dictionary"""
    from units import Hero, Unit

    # Special case for Heroes, who need to use a subclass that doesn't check abilities for actions
    if kwargs.get('type', None) == "Hero":
        return Hero(**kwargs)
    else:
        return Unit(**kwargs)
