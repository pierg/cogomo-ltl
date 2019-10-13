"""Contract module defines a contract class to store contract data attributes and a contracts class
to store all system contracts and overall system alphabet"""
import itertools
from LTL_contracts.src.operations import *
from LTL_contracts.src.contract import *
from collections import OrderedDict
from z3 import *

class Cgt(Contract):
    """
    Contract-based Goal Tree

    Attributes:
        contracts: a list of contract objects
        alphabet: a list of tuples containing the shared alphabet among all contracts
    """
    def __init__(self):
        """Initialize a contracts object"""

        super().__init__()

        # List of children and its relationship with them (COMPOSITION / CONJUNCTION)
        self.sub_cgts = None
        self.sub_operation = None

        # Parent cgt and its relation (COMPOSITION / CONJUNCTION)
        self.parent_cgt = None
        self.parent_operation = None

    def set_parent(self, parent_cgt, parent_operation):
        self.parent_cgt = parent_cgt
        self.parent_operation = parent_operation

    def get_subcgts_ops(self):
        return self.sub_cgts, self.sub_operation
    
    
def compose_cgts(contracts_to_compose, name=None):
    """
    :param name: Name of the cgt
    :param contracts: List of contracts to compose
    :return: True, composed_cgts if successful
    """
    contracts = list(contracts_to_compose)
    contracts = {}

    cgt_list = []
    for contract in contracts_to_compose:
        cgt_list.append(Cgt(contract))
        contracts[contract.get_name()] = contract

    composed_contracts = composition(contracts_to_compose)

    # # Creating a new Goal parent
    # composed_cgt = Cgt()
    #
    # # Connecting children to the parent
    # for cgt in cgts:
    #     cgt.set_parent(composed_cgt, "COMPOSITION")
    #
    # return True, composed_cgt


def conjoin_cgts(cgts, name):
    conjoined_contracts = []

    for cgt in cgts:
        conjoined_contracts.append(cgt.get_contracts())
    # Flattening list
    conjoined_contracts = [item for sublist in conjoined_contracts for item in sublist]

    sat = conjoin_contracts(conjoined_contracts)
    if not sat:
        print("conjoin failed")
        return False

    # Creating a new Goal parent
    conjoined_cgt = Cgt(name, conjoined_contracts,
                               sub_cgts=cgts,
                               sub_operation="CONJUNCTION")

    # Connecting children to the parent
    for cgt in cgts:
        cgt.set_parent(conjoined_cgt, "CONJUNCTION")

    return conjoined_cgt