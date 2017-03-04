"""
Used to deserialize and serialize json
"""

# from .dolphin import load, loads, dump, dumps
from .dolphin2 import loads, load, dump, dumps, empty
from .dynamic_class import make_dynamic_class

__author__ = 'benjamin.c.yan'
__all__ = ["load", "loads", "dump", "dumps", "make_dynamic_class"]
