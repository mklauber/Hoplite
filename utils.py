from os import path

class HopliteError(Exception):
    pass

DATA_DIR = path.join(path.dirname(__file__), 'data/')

def data_file(name):
    """Easily and centrally control where data files are"""
    return path.join(DATA_DIR, name)

def all_subclasses(cls):
    """Many times we create instances of Subclasses from a super class.  This is helpful for that."""
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]
                                   

def Counter():
    i = 0
    while True:
        yield i
        i += 1                               
