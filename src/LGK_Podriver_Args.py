"""
LGK_Podriver_Vars:
Longecko Podriver Variables
By Avastrator
2025-03-23 10:39:50
"""
def _init():
    global _global_args
    _global_args = {}
 
def set(name, value):
    _global_args[name] = value

def get(name, default=None):
    try:
        return _global_args[name]
    except KeyError:
        return default


def pop(name):
    try:
        return _global_args.pop(name)
    except KeyError:
        return None