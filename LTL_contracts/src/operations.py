"""Operations module provides LTL operations to test contracts"""

from LTL_contracts.src import contract
from LTL_contracts.src.core import *


def compatibility(contract):
    """Checks the compatibility of a contract object

    Args:
        contract: a contract object

    Returns:
        A string LTL expression that checks the compatibility of the input
    """
    return _ltl_inv(contract.get_assumptions())

def consistency(contract):
    """Checks the consistency of a contract object

    Args:
        contract: a contract object

    Returns:
        A string LTL expression that checks the consistency of the input
    """
    return _ltl_inv(contract.get_guarantees())


def satisfiability(contract):
    """Checks the satisfiability of a contract object

    Args:
        contract: a contract object

    Returns:
        A string LTL expression that checks the satisfiability of the input
    """
    return _ltl_inv(_and(contract.get_assumptions(), contract.get_guarantees()))



def refinement(acontract, bcontract):
    """Checks if acontract refines bcontract

    Args:
        acontract: a contract object
        bcontract: a contract object

    Returns:
        A string LTL expression that checks if acontract refines bcontract
    """
    return _ltl(_and(_imply(bcontract.get_assumptions(), acontract.get_assumptions()),
                     _imply(acontract.get_guarantees(), bcontract.get_guarantees())))


def inclusion(aproposition, bproposition):
    """Checks if aproposition is included bproposition

    Args:
        aproposition: a logic proposition
        bproposition: a logic proposition

    Returns:
        A string LTL expression that checks if aproposition is included in bproposition
    """
    return _ltl(_imply(aproposition, bproposition))

def saturation(contract):
    """Perform a saturation operation on a contract

    Args:
        contract: an unsaturated contract object
    """
    contract.guarantees = [_imply(contract.get_assumptions(), g) for g in contract.guarantees]

def composition(contracts):
    """Perform a composition operation on a list of contracts

    Args:
        contracts: a list of contract objects

    Returns:
        A contract object that is the composition of whole list
    """
    contracts = list(contracts)
    if len(contracts) == 1:
        return contracts[0]
    else:
        comp = contract.Contract()
        comp.add_name(contracts[0].name + '_comp_' + contracts[1].name)
        comp.add_variables(_merge(contracts[0].variables, contracts[1].variables))
        comp.add_assumption(_or(_and(contracts[0].get_assumptions(), contracts[1].get_assumptions()),
                            _inv(_and(contracts[0].get_guarantees(), contracts[1].get_guarantees()))))
        comp.add_guarantee(_and(contracts[0].get_guarantees(), contracts[1].get_guarantees()))
        contracts.pop(0) #remove first element in list
        contracts[0] = comp #replace "new" first element with conj
        return composition(contracts)


def simplify(variables, assumptions, guarantees):
    """
    Check if any of the guarantee is included in any of the assumptions
    :param assumption: list of assumptions
    :param gurantee: list of guarantees
    :return: (list of assumptions simplified, list of guarantees simplified)
    """

    simplified_assumptions = []
    simplified_guarantees = []

    for i, assumption in enumerate(assumptions):
        for j, guarantee in enumerate(guarantees):
            # check if all the behaviours of the assumptions are included in the guarantees
            # if not, then add the assumptions, otherwise simplify them
            if not check_inclusion(variables, guarantee, assumption):
                simplified_assumptions.append(assumption)
                simplified_guarantees.append(guarantee)

    return simplified_assumptions, simplified_guarantees


def composition_simplify(contracts):
    """Perform a composition operation on a list of contracts

    Args:
        contracts: a list of contract objects

    Returns:
        A contract object that is the composition of whole list
    """
    variables = []
    for contract in contracts:
        variables = list(set(variables) | set(contract.variables))

    contracts = list(contracts)
    # list of list of assumptions for each contract involved in the composition
    assumptions = [contract.get_assumptions_list() for contract in contracts]

    # list of list of guarantees for each contract involved in the composition
    guarantees = [contract.get_guarantees_list() for contract in contracts]

    simplified_assumptions = []
    simplified_guarantees_orneg = []

    for i, assumption in enumerate(assumptions):
        for j, guarantee in enumerate(guarantees):
            if i != j:
                simplified_a, simplified_g = simplify(variables, assumption, guarantee)
                simplified_assumptions.extend(simplified_a)
                simplified_guarantees_orneg.extend(simplified_g)

    comp = Contract()
    name = ""
    for i, contract in enumerate(contracts):
        name += contract.name
        if i < len(contracts):
            name += "_comp_"

    comp.add_name(name)
    comp.add_variables(variables)
    comp.add_assumptions(simplified_assumptions)
    comp.add_assumptions_orneg(simplified_guarantees_orneg)
    comp.add_guarantees(guarantees)

    return comp

def conjunction(contracts):
    """Takes the conjunction of a list of contracts

    Args:
        contracts: a list of contract objects

    Returns:
        A contract object that is the conjunction of whole list
    """
    if len(contracts) == 1:
        return contracts[0]
    else:
        conj = contract.Contract()
        conj.add_name(contracts[0].name + "_conj_" + contracts[1].name)
        conj.add_variables(_merge(contracts[0].variables, contracts[1].variables))
        conj.add_assumption(_or(contracts[0].get_assumptions(), contracts[1].get_assumptions()))
        conj.add_guarantee(_and(contracts[0].get_guarantees(), contracts[1].get_guarantees()))
        contracts.pop(0) #remove first element in list
        contracts[0] = conj #replace "new" first element with conj
        return conjunction(contracts)

def _merge(alist, blist):
    """Merges input lists and removes duplicates"""
    return list(set(alist) | set(blist))

def _ltl(astr):
    """Applies an inverted LTLSPEC wrapper to the input string"""
    return '\tLTLSPEC ' + astr + ';\n'

def _ltl_inv(astr):
    """Applies an inverted LTLSPEC wrapper to the input string"""
    return '\tLTLSPEC !' + astr + ';\n'

def _and(astr, bstr):
    """Returns logical and of astr and bstr"""
    # TODO: string equality, astr and bstr might contain more than TRUE
    if 'TRUE' in astr:
        return bstr
    if 'TRUE' in bstr:
        return astr
    return '(' + astr + ' & ' + bstr + ')'

def _or(astr, bstr):
    """Returns logical or of astr and bstr"""
    return '(' + astr + ' | ' + bstr + ')'

def _imply(astr, bstr):
    """Returns logical implication of bstr by astr"""
    return '(' + astr + ' -> ' + bstr + ')'

def _inv(astr):
    """Returns logical not of input"""
    return '!' + astr
