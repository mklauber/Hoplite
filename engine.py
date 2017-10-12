from reactions import REACTIONS
from actions import CreateAction
import json

import logging
logger = logging.getLogger(__name__)

class State(dict):
    def __init__(self):
        self.actors = []

    def __setitem__(self, key, value):
        key = (int(key[0]), int(key[1]))
        super(State, self).__setitem__(key, value)

    def find(self, target):
        for key, value in self.items():
            if value == target:
                return key
        raise KeyError()

    def __str__(self):
        return "Actors: %s\nGrid: %s" % (self.actors, super(State, self).__str__())
        

class Engine(object):
    def __init__(self, history):
        self.past = []
        self.future = history
        self.state = State()
        self.listeners = set()
        
        #self.fast_forward()
        
    def fast_forward(self):
        """Execute any remaining future items"""
        while self.future != []:
            self.step_forward()

    def rewind(self):
        """Rewind all past turns"""
        while self.past != []:
            self.step_backward()

    def step_backward(self):
        if len(self.past) == 0:
            return
        turn = self.past.pop()
        if len(self.state.actors) > 0:
            actor = self.state.actors.pop()
            self.state.actors.insert(0, actor)
        
        for action in reversed(turn):
            action.rollback(self.state)
        self.future.insert(0, turn)
            
    def step_forward(self):
        if len(self.future) == 0:
            return
        turn = self.future.pop(0)
        if len(self.state.actors) > 0:
            actor = self.state.actors.pop(0)
            self.state.actors.append(actor)
        for action in turn:
            self.emit(self.state, action)
            action.execute(self.state)
        self.past.append(turn)

    
    def emit(self, state, action):
        """Announce to any interested listeners each action and the state before the action"""
        for listener in self.listeners:
            listener(state, action)
    
    def record(self, overwrite=False):
        if overwrite == False and self.future != []:
            raise HopliteError("Cannot record a turn when future turns exist unless the overwrite flag is True")
        
        # Cycle the actors
        actor = self.state.actors.pop(0)
        self.state.actors.append(actor)
                
        actions = [actor.get_action(self.state)]
        turn = []
        while len(actions) != 0:
            action = actions.pop(0)
            if action == None:
                continue
            reactions = determine_reactions(action, self.state)
            actions = reactions + actions
            action.execute(self.state)
            turn.append(action)
        
        self.past.append(turn)
        self.step_backward()
        self.fast_forward()
 

def determine_reactions(action, state):
    reactions = []
    for behavior in REACTIONS:
        reactions.extend(behavior(action, state))
    return reactions

def load_level(filename):
    result = []
    with open(filename, 'r') as f:
        level = json.loads(f.read())
    for turn in level:
        computed = []
        for action in turn:
            computed.append(CreateAction(action))
        result.append(computed)
    return result


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    def listener(state, action):
        print state
        print action
        print
    
    level = load_level('data/level1.json')
    e = Engine(level)
    
    e.listeners.add(listener)
    e.fast_forward()
    while len(set(u['team'] for u in e.state.values())) > 1:
        e.record()





