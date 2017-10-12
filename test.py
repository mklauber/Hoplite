import actions
from units import Unit
from engine import State



def parse_spawn(command):
    action, actor, x, y = command.split(" ")
    return actions.Spawn(Unit.create({"type": actor}), (int(x),int(y)))
    


def parse(command, state):
    action, _ = command.split(" ", 1)
    if action == "spawn":
        return parse_spawn(command)
   
    

if __name__ == '__main__':
    state = State()
    turns = []
    turn = []
    while True:
        command = raw_input("Next Action: ")
        if command == "stop":
            break
        action = parse(command, state)
        print "Action: ", action
        if action != None:
            print "running action"
            action.execute(state)
        print state
