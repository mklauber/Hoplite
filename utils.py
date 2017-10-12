class HopliteError(Exception):
    pass

def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]
                                   

def Counter():
    i = 0
    while True:
        yield i
        i += 1                               
