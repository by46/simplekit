"""
Used to deserialize and serialize json
"""

# from .dolphin import load, loads, dump, dumps
from .dolphin import make_dynamic_class
from .dolphin2 import loads, load, dump, dumps, empty

__author__ = 'benjamin.c.yan'
__all__ = ["load", "loads", "dump", "dumps", "make_dynamic_class"]
