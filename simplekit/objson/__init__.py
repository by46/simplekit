"""
Used to deserialize and serialize json
"""

from .dolphin import load, loads, dump, dumps
from .dolphin import make_dynamic_class
from .dolphin2 import loads as loads2, load as load2, dump as dump2, dumps as dumps2

__author__ = 'benjamin.c.yan'
__all__ = ["load", "loads", "dump", "dumps", "make_dynamic_class"]
