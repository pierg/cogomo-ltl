#!/usr/bin/env python
"""Contract module defines a contract class to store contract data attributes and a contracts class
to store all system contracts and overall system alphabet"""
import itertools
from collections import OrderedDict
from z3 import *
from Z3_contracts.src.contract_operations import *


class FailComposition(Exception):
    print("Composition Failed")



class Cgt(object):
    """
    Contract-based Goal Tree

    Attributes:
        contracts: a list of contract objects
        alphabet: a list of tuples containing the shared alphabet among all contracts
    """
    def __init__(self,
                 name="no_name",
                 contracts=None,
                 sub_goals=None,
                 sub_operation=None,
                 parent_goal=None,
                 parent_operation=None):
        """Initialize a contracts object"""

        self.name = name

        # contracts in conjunction
        if not isinstance(contracts, list):
            self.contracts = [contracts]
        else:
            self.contracts = contracts

        # List of children and its relationship with them (COMPOSITION / CONJUNCTION)
        self.sub_goals = sub_goals
        self.sub_operation = sub_operation

        # Parent goal and its relation (COMPOSITION / CONJUNCTION)
        self.parent_goal = parent_goal
        self.parent_operation = parent_operation

    def set_parent(self, parent_goal, parent_operation):
        self.parent_goal = parent_goal
        self.parent_operation = parent_operation

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_subgoals_ops(self):
        return self.sub_goals, self.sub_operation

    def get_contracts(self):
        return self.contracts


    def __str__(self, level=0):
        """Override the print behavior"""
        ret = "\t" * level + repr(self.name) + "\n"
        for n, contract in enumerate(self.contracts):
            if n > 0:
                ret += "\t" * level + "\t/\\ \n"
            ret += "\t" * level + "A:\t\t" + \
                   ', '.join(str(x) for x in contract.get_assumptions()).replace('\n', ' ').replace(' ', '') + "\n"
            ret += "\t" * level + "G:\t\t" + \
                   ', '.join(str(x) for x in contract.get_guarantees()).replace('\n', ' ').replace(' ', '') + "\n"
            # if contract.is_abstracted():
            #     ret += "\t" * level + "G_abs:\t" + \
            #            ', '.join(str(x) for x in contract.get_abstract_guarantees()).replace('\n', ' ').replace(' ',
            #                                                                                                     '') + "\n"
        ret += "\n"
        if self.sub_goals is not None and len(self.sub_goals) > 0:
            ret += "\t" * level + "\t" + self.sub_operation + "\n"
            level += 1
            for child in self.sub_goals:
                ret += child.__str__(level + 1)
        return ret

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)
    
    
def compose_goals(list_of_cgt, name=None, abstract_on_guarantees=None):
    """

    :param name: Name of the goal
    :param contracts: List of contracts to compose
    :return: True, composed_goals if successful
    """

    contracts = {}
    abstracted_contracts = {}

    for cgt in list_of_cgt:
        contracts[cgt.get_name()] = cgt.get_contracts()

    if name is None:
        name = '_'.join("{!s}".format(key) for (key, val) in list(contracts.items()))

    composition_contracts = (dict(list(zip(contracts, x))) for x in itertools.product(*iter(contracts.values())))

    composed_contract_list = []
    for contracts in composition_contracts:
        satis, composed_contract = compose_contracts(contracts, abstract_on_guarantees=abstract_on_guarantees)
        if not satis:
            raise FailComposition
        composed_contract_list.append(composed_contract)

    # Creating a new Goal parent
    composed_goal = Cgt(name, composed_contract_list,
                              sub_goals=list_of_cgt,
                              sub_operation="COMPOSITION")

    # Connecting children to the parent
    for goal in list_of_cgt:
        goal.set_parent(composed_goal, "COMPOSITION")

    return composed_goal


def conjoin_goals(goals, name):
    conjoined_contracts = []

    for goal in goals:
        conjoined_contracts.append(goal.get_contracts())
    # Flattening list
    conjoined_contracts = [item for sublist in conjoined_contracts for item in sublist]

    sat = conjoin_contracts(conjoined_contracts)
    if not sat:
        print("conjoin failed")
        return False

    # Creating a new Goal parent
    conjoined_goal = Cgt(name, conjoined_contracts,
                               sub_goals=goals,
                               sub_operation="CONJUNCTION")

    # Connecting children to the parent
    for goal in goals:
        goal.set_parent(conjoined_goal, "CONJUNCTION")

    return conjoined_goal