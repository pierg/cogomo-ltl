#!/usr/bin/env python
"""Core module defines the core workflow functions of the LTL contract checker tool"""

import subprocess, re
from Z3_contracts.src.cgt import *
from Z3_contracts.src.contract import Contract, Contracts

# contract file attributes
TAB_WIDTH = 2
FILE_HEADER_INDENT = 0
CONSTANTS_HEADER_INDENT = 1
CONSTANTS_DATA_INDENT = 2
CGT_HEADER_INDENT = 1
CGT_DATA_INDENT = 2
CONTRACT_HEADER_INDENT = 1
CONTRACT_DATA_INDENT = 2
CHECK_DATA_INDENT = 1
COMMENT_CHAR = '##'
ASSIGNMENT_CHAR = ':='
OPERATORS = '<|>|!=| == | >= | <= | \|\| |&&'
CONTRACT_HEADER = 'CONTRACT'
CONSTANTS_HEADER = 'CONSTANTS'
CGT_HEADER = 'CGT'
CGT_CONJUNCTION_HEADER = 'CONJUNCTION'
CGT_COMPOSITION_HEADER = 'COMPOSITION'
CONTRACT_NAME_HEADER = 'NAME'
CGT_NAME_HEADER = 'NAME'
CGT_TREE_HEADER = 'TREE'
CGT_END_TREE = 'ENDTREE'
CGT_END_OPERATION = 'ENDTREE|CONJUNCTION|COMPOSITION'
CONTRACT_VARIABLES_HEADER = 'VARIABLES'
CONTRACT_ASSUMPTIONS_HEADER = 'ASSUMPTIONS'
CONTRACT_GUARANTEES_HEADER = 'GUARANTEES'


def parse(specfile):
    """Parses the system specification file and returns the contracts and checks

    Args:
        specfile: a string input file name for the system specification file

    Returns:
        A tuple containing a contracts object and a checks object
    """
    contract = Contract() # contract and check holders
    cgt = Cgt()

    contracts_dictionary = {}
    cgt_dictionary = {}

    contracts = Contracts()
    constants = {}
    file_header = '' # file header line contents
    contract_header = '' # contract header line contents
    cgt_header = '' # cgt header line contents

    with open(specfile, 'r') as ifile:
        for line in ifile:
            line, ntabs = _clean_line(line)

            # skip empty lines
            if not line:
                continue

            # parse file header line
            elif ntabs == FILE_HEADER_INDENT:
                # store previously parsed contract
                if CONTRACT_HEADER in file_header:
                    if contract.is_full():
                        # contract.saturate_guarantees()
                        contracts.add_contract(contract)
                        contracts_dictionary[contract.get_name()] = contract
                        cgt_dictionary[contract.get_name()] = Cgt(contract.get_name(), contracts=contract)
                    else: # (TODO) add error - contract params incomplete
                        pass
                # parse file headers
                if CONSTANTS_HEADER in line:
                    file_header = line
                elif CONTRACT_HEADER in line:
                    if file_header:
                        contract = Contract()
                    file_header = line
                elif CGT_HEADER in line:
                    file_header = line
                else: # (TODO) add error - unexpected file heading
                    pass

            # parse contract and check data
            else:
                if CONSTANTS_HEADER in file_header:
                    if ntabs == CONSTANTS_DATA_INDENT:
                        var, init = line.split(ASSIGNMENT_CHAR, 1)
                        constants[var.strip()] = int(init.strip())
                elif CONTRACT_HEADER in file_header:
                    if ntabs == CONTRACT_HEADER_INDENT:
                        contract_header = line
                    elif ntabs == CONTRACT_DATA_INDENT:
                        if CONTRACT_NAME_HEADER in contract_header:
                            contract.add_name(line.strip())
                            for key, value in constants.items():
                                contract.add_constant((key, value))
                        elif CONTRACT_VARIABLES_HEADER in contract_header:
                            var, init = line.split(ASSIGNMENT_CHAR, 1)
                            contract.add_variable((var.strip(), init.strip()))
                        elif CONTRACT_ASSUMPTIONS_HEADER in contract_header:
                            list_of_variables = re.split(OPERATORS, line)
                            list_stripped = []
                            for elem in list_of_variables:
                                list_stripped.append(elem.strip())
                            for variable in list_stripped:
                                regx = re.compile(variable + '\s|' + variable + '$')
                                line = regx.sub("self.variables['" + variable + "']", line)
                            contract.add_assumption(line.strip())
                        elif CONTRACT_GUARANTEES_HEADER in contract_header:
                            list_of_variables = re.split(OPERATORS, line)
                            list_stripped = []
                            for elem in list_of_variables:
                                list_stripped.append(elem.strip())
                            for variable in list_stripped:
                                regx = re.compile(variable + '\s|' + variable + '$')
                                line = regx.sub("self.variables['" + variable + "']", line)
                            contract.add_guarantee(line.strip())
                        else: # (TODO) add error - unexpected contract heading
                            pass
                    else: # (TODO) add error - unexpected indentation
                        pass
                elif CGT_HEADER in file_header:
                    if ntabs == CGT_HEADER_INDENT:
                        cgt_header = line
                    elif ntabs == CGT_DATA_INDENT:
                        if CGT_NAME_HEADER in cgt_header:
                            cgt.set_name(line.strip())
                        elif CGT_TREE_HEADER in cgt_header:
                            cgt_header = line
                            while CGT_END_TREE not in line:
                                if CGT_COMPOSITION_HEADER in line:
                                    contract_to_compose = []
                                    line += 1
                                    while not re.match(CGT_END_OPERATION, line):
                                        line = line + 1
                                        contract_to_compose.append(contracts.get_contract(line.strip()))
                                    compose_goals(contract_to_compose)


    return contracts_dictionary, cgt_dictionary


def _clean_line(line):
    """Returns a comment-free, tab-replaced line with no whitespace and the number of tabs"""
    line = line.split(COMMENT_CHAR, 1)[0] # remove comments
    line = line.replace('\t', ' ' * TAB_WIDTH) # replace tabs with spaces
    return line.strip(), _line_indentation(line)

def _line_indentation(line):
    """Returns the number of indents on a given line"""
    return (len(line) - len(line.lstrip(' '))) / TAB_WIDTH
