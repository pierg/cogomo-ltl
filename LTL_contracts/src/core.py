"""Core module defines the core workflow functions of the LTL contract checker tool"""

import subprocess, re
from LTL_contracts.src.cgt import Cgt
from LTL_contracts.src.contract import Contract, Contracts
from LTL_contracts.src.check import Compatibility, Consistency, Refinement, Checks, Satisfiability

# contract file attributes
TAB_WIDTH = 4
FILE_HEADER_INDENT = 0
CONTRACT_HEADER_INDENT = 1
CONTRACT_DATA_INDENT = 2
CHECK_DATA_INDENT = 1
CGT_HEADER_INDENT = 1
CGT_DATA_INDENT = 2
COMMENT_CHAR = '##'
ASSIGNMENT_CHAR = ':='
CHECKS_HEADER = 'CHECKS'
CONTRACT_HEADER = 'CONTRACT'
CONTRACT_NAME_HEADER = 'NAME'
CONTRACT_VARIABLES_HEADER = 'VARIABLES'
CONTRACT_ASSUMPTIONS_HEADER = 'ASSUMPTIONS'
CONTRACT_GUARANTEES_HEADER = 'GUARANTEES'
COMPATIBILITY_COMP_CHECK = 'COMPATIBILITY_COMP'
COMPATIBILITY_CONJ_CHECK = 'COMPATIBILITY_CONJ'
CONSISTENCY_COMP_CHECK = 'CONSISTENCY_COMP'
CONSISTENCY_CONJ_CHECK = 'CONSISTENCY_CONJ'
CGT_HEADER = 'CGT'
CGT_CONJUNCTION_HEADER = 'CONJUNCTION'
CGT_COMPOSITION_HEADER = 'COMPOSITION'
CGT_NAME_HEADER = 'NAME'
CGT_TREE_HEADER = 'TREE'
CGT_END_TREE = 'ENDTREE'
CGT_END_OPERATION = 'ENDTREE|CONJUNCTION|COMPOSITION'
REFINEMENT = 'REFINEMENT'
SATISFIABILITY = 'SATISFIABILITY'


def parse(specfile):
    """Parses the system specification file and returns the contracts and checks

    Args:
        specfile: a string input file name for the system specification file

    Returns:
        A tuple containing a contracts object and a checks object
    """
    cgt, contracts, checks = Cgt(), Contracts(), Checks()  # returned contracts and checks
    contract = Contract()  # contract and check holders
    file_header = ''  # file header line contents
    contract_header = ''  # contract header line contents
    cgt_header = ''

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
                        contract.saturate_guarantees()
                        contracts.add_contract(contract)
                    else:  # (TODO) add error - contract params incomplete
                        pass
                # parse file headers
                if CONTRACT_HEADER in line:
                    if file_header:
                        contract = Contract()
                    file_header = line
                elif CHECKS_HEADER in line:
                    file_header = line
                elif CGT_HEADER in line:
                    file_header = line
                else:  # (TODO) add error - unexpected file heading
                    pass

            # parse contract and check data
            else:
                if CONTRACT_HEADER in file_header:
                    if ntabs == CONTRACT_HEADER_INDENT:
                        contract_header = line
                    elif ntabs == CONTRACT_DATA_INDENT:
                        if CONTRACT_NAME_HEADER in contract_header:
                            contract.add_name(line.strip())
                        elif CONTRACT_VARIABLES_HEADER in contract_header:
                            var, init = line.split(ASSIGNMENT_CHAR, 1)
                            contract.add_variable((var.strip(), init.strip()))
                        elif CONTRACT_ASSUMPTIONS_HEADER in contract_header:
                            contract.add_assumption(line.strip())
                        elif CONTRACT_GUARANTEES_HEADER in contract_header:
                            contract.add_guarantee(line.strip())
                        else:  # (TODO) add error - unexpected contract heading
                            pass
                    else:  # (TODO) add error - unexpected indentation
                        pass
                elif CHECKS_HEADER in file_header:
                    if ntabs == CHECK_DATA_INDENT:
                        check_type, check_contracts = line.split(')', 1)[0].split('(', 1)
                        if "," in check_contracts:
                            check_contracts = [contracts.get_contract(
                                contract.strip()) for contract in check_contracts.split(',')]
                            if COMPATIBILITY_COMP_CHECK in check_type.upper():
                                check = Compatibility('composition', check_contracts)
                            elif COMPATIBILITY_CONJ_CHECK in check_type.upper():
                                check = Compatibility('conjunction', check_contracts)
                            elif CONSISTENCY_COMP_CHECK in check_type.upper():
                                check = Consistency('composition', check_contracts)
                            elif CONSISTENCY_CONJ_CHECK in check_type.upper():
                                check = Consistency('conjunction', check_contracts)
                            elif REFINEMENT in check_type.upper():
                                check = Refinement(check_contracts)
                            else:  # (TODO) add error - unrecognized check
                                pass
                        else:
                            check_contract = contracts.get_contract(check_contracts)
                            if SATISFIABILITY in check_type.upper():
                                check = Satisfiability([check_contract])
                        checks.add_check(check)
                    else:  # (TODO) add error - unexpected indentation
                        pass
                elif CGT_HEADER in file_header:
                    if ntabs == CGT_HEADER_INDENT:
                        cgt_header = line
                    elif ntabs == CGT_DATA_INDENT:
                        if CGT_NAME_HEADER in cgt_header:
                            pass
                        elif CGT_TREE_HEADER in cgt_header:
                            while CGT_END_TREE not in line:
                                if CGT_COMPOSITION_HEADER in line:
                                    contract_to_compose = []
                                    line += 1
                                    while not re.match(CGT_END_OPERATION, line):
                                        line = line + 1
                                        contract_to_compose.append(contracts.get_contract(line.strip()))


                        else:  # (TODO) add error - unexpected contract heading
                            pass
                    else:  # (TODO) add error - unexpected indentation
                        pass

    return contracts, checks


def generate(contracts, checks, smvfile):
    """Generates a NuSMV file with configured variable declarations and LTL checks

    Args:
        contracts: a contracts object containing all the contracts in a system
        checks: a checks object containing all the desired checks on the system
        smvfile: a string name for the generated NuSMV file
    """
    with open(smvfile, 'w') as ofile:

        # write module heading declaration
        ofile.write('MODULE main\n')

        # write variable type declarations
        ofile.write('VAR\n')
        for (var, _) in contracts.get_alphabet():
            ofile.write('\t' + var + ': boolean;\n')

        # write variable assignment declarations
        ofile.write('ASSIGN\n')
        for (var, init) in contracts.get_alphabet():
            ofile.write('\tinit(' + var + ') := ' + init + ';\n')
        ofile.write('\n')

        # write LTL specifications declarations for each check
        for check in checks.checks:
            ofile.write(check.get_ltl())


def run(smvfile, checks):
    """runs the set of contracts and checks through NuSMV and parses the results to return to the user"""

    # Initialize an array to hold the results of the checks
    results = []

    # create the command and run in terminal
    output = subprocess.check_output(['NuSMV', smvfile], encoding='UTF-8').splitlines()

    # Get rid of all initial notes, warnings and blank lines
    output = [x for x in output if not (x[:3] == '***' or x[:7] == 'WARNING' or x == '')]

    # Iterate through all remaining lines of output, stopping at each "-- specification line to parse it"
    result_num = -1  # Counter to keep track of what result you're looking at
    in_result = False  # Flag to track if you're in a counterexample output
    temp_counterexample = []
    counterexamples = {}

    for line in output:
        # If this line is going to indicate whether or not a LTL spec is true/false
        if line[:16] == '-- specification':
            check_type = checks.checks[result_num].check_type
            print("\n" + check_type + " check...")
            print(line)
            if in_result:
                in_result = False
                counterexamples[result_num] = temp_counterexample
                temp_counterexample = []
            if 'is false' in line:
                result_num += 1
                if check_type == 'refinement':
                    results.append(False)
                    print(checks.checks[result_num].get_contracts()[0].get_name() +
                          " is NOT a refinement of " + checks.checks[result_num].get_contracts()[1].get_name())
                elif check_type == 'satisfiability':
                    results.append(False)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are NOT satisfiabiles")
                elif check_type == 'compatibility':
                    results.append(True)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are compatible")
                elif check_type == 'consistency':
                    results.append(True)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are consistent")
            elif 'is true' in line:
                result_num += 1
                if check_type == 'refinement':
                    results.append(True)
                    print(checks.checks[result_num].get_contracts()[0].get_name() +
                          " is a refinement of " + checks.checks[result_num].get_contracts()[1].get_name())
                elif check_type == 'satisfiability':
                    results.append(True)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are satisfiabiles")
                elif check_type == 'compatibility':
                    results.append(False)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are NOT compatible")
                elif check_type == 'consistency':
                    results.append(False)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are NOT consistent")
            print("")

        # If you are currently in a counterexample
        if in_result:
            temp_counterexample.append(line)

        # If the next line is going to be the start of a counterexample, set the in_result flag
        if line == 'Trace Type: Counterexample ':
            in_result = True

    if in_result:
        in_result = False
        counterexamples[result_num] = temp_counterexample
        temp_counterexample = []

    for x in range(result_num + 1):
        print("Result of checking:", checks.checks[x])
        if checks.checks[x].check_type == 'refinement':
            print('The refinement is', results[x])
        if checks.checks[x].check_type == 'satisfiability':
            print('The satisfiability is', results[x])
        else:
            print('Statement is', results[x])
            if results[x] == True:
                print('Example:')
                for y in counterexamples[x]:
                    print(y)
                print('')

    return results


def _clean_line(line):
    """Returns a comment-free, tab-replaced line with no whitespace and the number of tabs"""
    line = line.split(COMMENT_CHAR, 1)[0]  # remove comments
    line = line.replace('\t', ' ' * TAB_WIDTH)  # replace tabs with spaces
    return line.strip(), _line_indentation(line)


def _line_indentation(line):
    """Returns the number of indents on a given line"""
    return (len(line) - len(line.lstrip(' '))) / TAB_WIDTH
