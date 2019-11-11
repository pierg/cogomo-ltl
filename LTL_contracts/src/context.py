"""Contract module defines a contract class to store contract data attributes and a contracts class
to store all system contracts and overall system alphabet"""
import itertools
from LTL_contracts.src.operations import *
from LTL_contracts.src.contract import *
from collections import OrderedDict
from check import *
from core import *
from z3 import *

from operations import *

from itertools import combinations


class PatternError(object):
    pass

class Context(Cgt):
    """
    General Context Class
    """
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.add_assumption("TRUE")



class Robot(Context):
    """
    Visit a set of locations in an unspecified order.
    """

    def __init__(self, name, weight_power=None):
        """
        :type lifting_power:
        """
        super().__init__(name)

        self.add_variable(('weight_power', "5..15"))
        self.add_guarantee(weight_power)


