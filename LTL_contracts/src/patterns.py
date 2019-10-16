"""Contract module defines a contract class to store contract data attributes and a contracts class
to store all system contracts and overall system alphabet"""
import itertools
from LTL_contracts.src.operations import *
from LTL_contracts.src.contract import *
from collections import OrderedDict
from check import *
from core import *
from z3 import *


class PatternError(object):
    pass

class Pattern(Cgt):
    """
    General Pattern Class
    """
    def __init__(self, name):
        super().__init__()
        self.name = name



class Visit(Pattern):
    """
    Visit a set of locations in an unspecified order.
    """

    def __init__(self, name, list_of_locations=None):
        """
        :type list_of_locations: list of location, each location is a boolean
        indicating if the robot is at that location
        """
        super().__init__(name)
        if list_of_locations is None:
            raise PatternError

        # TODO: add assumptions, e.g. the robot cannot be in the same location at the same time?
        self.add_assumption("TRUE")
        for location in list_of_locations:
            self.add_variable((location, 'FALSE'))
            self.add_guarantee("F(" + location + ")")

class SequencedVisit(Pattern):
    """
    Visit a set of locations in sequence, one after the other.
    """

    def __init__(self, name, list_of_locations=None):
        """
        :type list_of_locations: list of location, each location is a boolean
        indicating if the robot is at that location
        """
        super().__init__(name)
        if list_of_locations is None:
            raise PatternError

        # TODO: add assumptions, e.g. the robot cannot be in the same location at the same time?
        self.add_assumption("TRUE")
        guarantee = "F("
        for n, location in enumerate(list_of_locations):
            self.add_variable((location, 'FALSE'))

            guarantee += location
            if n == len(list_of_locations) - 1:
                for _ in range(len(list_of_locations)):
                    guarantee += ")"
            else:
                guarantee += " & F("

        self.add_guarantee(guarantee)


class OrderedVisit(Pattern):
    """
    Sequence visit does not forbid to visit a successor location before its predecessor, but only that after the
    predecessor is visited the successor is also visited. Ordered visit forbids a successor to be visited
    before its predecessor.
    """

    def __init__(self, name, list_of_locations=None):
        """
        :type list_of_locations: list of location, each location is a boolean
        indicating if the robot is at that location
        """
        super().__init__(name)
        if list_of_locations is None:
            raise PatternError

        # TODO: add assumptions, e.g. the robot cannot be in the same location at the same time?
        self.add_assumption("G(!a U d)")
        guarantee = "F("
        for n, location in enumerate(list_of_locations):
            self.add_variable((location, 'FALSE'))

            guarantee += location
            if n == len(list_of_locations) - 1:
                for _ in range(len(list_of_locations)):
                    guarantee += ")"
            else:
                guarantee += " & F("

        self.add_guarantee(guarantee)

        for n, location in enumerate(list_of_locations):
            if n < len(list_of_locations)-1:
                self.add_guarantee("!" + list_of_locations[n+1] + " U " + list_of_locations[n])

class GlobalAvoidance(Pattern):
    """
    Visit a set of locations in an unspecified order.
    """

    def __init__(self, name, list_of_locations=None):
        """
        :type list_of_locations: list of location, each location is a boolean
        indicating if the robot is at that location
        """
        super().__init__(name)
        if list_of_locations is None:
            raise PatternError

        # TODO: add assumptions, e.g. the robot cannot be in the same location at the same time?
        self.add_assumption("TRUE")
        for location in list_of_locations:
            self.add_variable((location, 'FALSE'))
            self.add_guarantee("!" + location + " -> G(!" + location + ")")


if __name__ == '__main__':

    smv_file = "nusmvfile.smv"

    visit_1 = OrderedVisit("visit1", ("a", "d"))
    # visit_2 = OrderedVisit("visit2", ("a", "d"))
    print(visit_1)
    # print(visit_2)
    check_1 = Checks()
    check_1.add_check(Satisfiability([visit_1]))
    generate(Contracts([visit_1]), check_1, smv_file)
    results = run(smv_file, check_1)
    print(results)
    #
    # seq_visit_1 = OrderedVisit("odervisit", ("a", "d", "e", "f"))
    # glob_avoidance = GlobalAvoidance("avoid", "g")
    #
    # print(seq_visit_1)
    #
    # contract_list = [visit_1, seq_visit_1, glob_avoidance]
    # contracts = Contracts(contract_list)
    #
    # checks = Checks()
    # checks.add_check(Compatibility("composition", contract_list))
    # checks.add_check(Consistency("composition", contract_list))
    #
    # smv_file = "nusmvfile.smv"
    # generate(contracts, checks, smv_file)
    # results = run(smv_file, checks)
    # print(results)
    # if not results[0]:
    #     print("The mission is not compatible, fix the assumptions")
    # if not results[1]:
    #     print("The mission is not consistent")
    # elif results[0] and results[1]:
    #     print("The mission specified is compatible and consistent, composing now..")
    #     mission = composition(contract_list)
    #     print(mission)