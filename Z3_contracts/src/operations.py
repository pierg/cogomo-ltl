#!/usr/bin/env python
"""Operations module provides LTL operations to test contracts"""
from z3 import *
from Z3_contracts.src.contract import *
from Z3_contracts.src.sat_checks import *

class WrongParametersError(Exception):
    """
    raised if the parameters passed are wrong
    """
    pass

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

def saturation(contract):
    """Perform a saturation operation on a contract

    Args:
        contract: an unsaturated contract object
    """
    contract.guarantees = [_imply(contract.get_assumptions(), g) for g in contract.guarantees]

def composition(contracts, abstract_on_guarantees=None):
    """Perform a composition operation on a list of contracts

    Args:
        contracts: a list of contract objects

    Returns:
        A contract object that is the composition of whole list
    """
    contracts_dictionary = contracts.get_contracts()

    variables = {}
    assumptions = {}
    guarantees = {}
    abstracted_guarantees = {}

    # Check if at least one contract is abstracted
    abstracted_contracts = False

    for name, contract in list(contracts_dictionary.items()):
        variables = _merge_two_dicts(variables, contract.get_variables())
        assumptions[name + "_assumptions"] = contract.get_assumptions()
        guarantees[name + "_guarantees"] = contract.get_guarantees()
        # if contract.is_abstracted():
        #     abstracted_contracts = True
        #     abstracted_guarantees[name + "_abstracted_guarantees"] = contract.get_abstract_guarantees()
        # else:
        #     abstracted_guarantees[name + "_abstracted_guarantees"] = contract.get_guarantees()

    # CHECK COMPATILITY
    satis, model = sat_check(assumptions)
    if not satis:
        print("The composition is uncompatible")
        print(("Fix the following assumptions:\n" + str(model)))
        return False, model

    # CHECK CONSISTENCY
    satis, model = sat_check(guarantees)
    if not satis:
        print("The composition is inconsistent")
        print(("Fix the following guarantees:\n" + str(model)))
        return False, model

    # CHECK SATISFIABILITY
    satis, model = sat_check(_merge_two_dicts(assumptions, guarantees))
    if not satis:
        print("The composition is unsatisfiable")
        print(("Fix the following conditions:\n" + str(model)))
        return False, model

    print("The composition is compatible, consistent and satisfiable. Composing now...")

    a_composition = list(assumptions.values())
    g_composition = list(guarantees.values())

    # Flatting the lists
    a_composition = [item for sublist in a_composition for item in sublist]
    g_composition = [item for sublist in g_composition for item in sublist]

    # Eliminating duplicates of assertions
    a_composition = list(dict.fromkeys(a_composition))
    g_composition = list(dict.fromkeys(g_composition))

    a_composition_simplified = a_composition[:]
    g_composition_simplified = g_composition[:]

    print(("Assumptions:\n\t\t" + str(a_composition_simplified)))
    print(("Guarantees:\n\n\t\t" + str(g_composition_simplified)))

    # List of guarantees used to simpolify assumptions, used later for abstraction
    g_elem_list = []
    # Compare each element in a_composition with each element in g_composition
    for a_elem in a_composition:
        for g_elem in g_composition:
            if is_contained_in(a_elem, g_elem):
                print(("Simplifying assumption " + str(a_elem)))
                a_composition_simplified.remove(a_elem)
                g_elem_list.append(g_elem)
                # g_composition_simplified.remove(g_elem)

    # Check for contract abstractions to be adjusted
    for guarantee in g_elem_list:
        for contract in list(contracts_dictionary.values()):
            if contract.is_abstracted():
                contract.abstract_guarantee_if_exists(guarantee)

    # Building the contract to return
    contract_composed = Contract()
    contract_composed.add_variables(variables)
    contract_composed.add_assumptions(a_composition_simplified)
    contract_composed.add_guarantees(g_composition_simplified)

    # Build the abstracted contract if there are other abstracted contracts
    if abstracted_contracts:
        g_composition = list(abstracted_guarantees.values())
        g_composition = [item for sublist in g_composition for item in sublist]
        g_composition = list(dict.fromkeys(g_composition))

        print(("Abstracted Guarantees:\n\n\t\t" + str(g_composition)))

        return True, Contract(a_composition_simplified, g_composition_simplified,
                              abstract_guarantees=g_composition)

    # Check for guarantee abstraction demanded by the designer
    if abstract_on_guarantees is not None:
        # Check the guarantees are an abstraction of the actual guarantees
        if is_contained_in(g_composition_simplified, abstract_on_guarantees):
            return True, Contract(a_composition_simplified, g_composition_simplified,
                                  abstract_guarantees=abstract_on_guarantees)
        else:
            raise AbstractionError

    return True, Contract(a_composition_simplified, g_composition_simplified)



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



def _merge_two_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


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
    return '(' + astr + ' & ' + bstr + ')'

def _or(astr, bstr):
    """Returns logical or of astr and bstr"""
    return Or(eval())

def _imply(astr, bstr):
    """Returns logical implication of bstr by astr"""
    return '(' + astr + ' -> ' + bstr + ')'

def _inv(astr):
    """Returns logical not of input"""
    return '!' + astr
