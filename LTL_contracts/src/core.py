"""Core module defines the core workflow functions of the LTL contract checker tool"""

import subprocess, re
from LTL_contracts.src.cgt import Cgt
from LTL_contracts.src.contract import Contract, Contracts
from LTL_contracts.src.check import Compatibility, Consistency, Refinement, Checks, Satisfiability, Inclusion

smv_file = "checks_smtfile.smv"

TAB_WIDTH = 4

class Incompatible(Exception):
    print("Incompatible Exception")

class Inconsistent(Exception):
    print("Inconsistency Exception")

class Unsatisfiable(Exception):
    print("Unsatisfiable Exception")


def check_inclusion(variables, aproposition, bproposition):
    """
    Check if the logical proposition in aproposition is included in bproposition
    :param variables:
    :param apropositioj:
    :param bproposition:
    :return: True or Falsee
    """

    checks = Checks()

    checks.add_check(Inclusion(aproposition, bproposition))

    generate(variables, checks, smv_file)

    results = run(smv_file, checks)

    print("RESULTS: " + str(results))

    return results[0]




def check_satisfiability(contract):
    """

    :param contract:
    :return:
    """
    checks = Checks()

    checks.add_check(Satisfiability([contract]))
    generate(Contracts([contract]).get_alphabet(), checks, smv_file)

    results = run(smv_file, checks)

    if False in results:
        raise Unsatisfiable



def check_compatibility_consistency(list_contracts):
    """
    Check for compatibility, consistency and satisfiability
    :param list_contracts:
    :return: (compatible, consistent)
    """
    checks = Checks()
    checks.add_check(Compatibility("composition", list_contracts))
    checks.add_check(Consistency("composition", list_contracts))

    generate(Contracts(list_contracts).get_alphabet(), checks, smv_file)
    results = run(smv_file, checks)

    if not results[0]:
        print("The contracts are not compatible, fix the assumptions")
        raise Incompatible
    if not results[1]:
        print("The contracts are not consistent")
        raise Inconsistent
    elif results[0] and results[1]:
        print("The contracts are compatible and consistent")


def generate(variables, checks, smvfile):
    """Generates a NuSMV file with configured variable declarations and LTL checks

    Args:
        variables: variables involved in the check
        checks: a checks object containing all the desired checks on the system
        smvfile: a string name for the generated NuSMV file
    """
    with open(smvfile, 'w') as ofile:

        # write module heading declaration
        ofile.write('MODULE main\n')

        # write variable type declarations
        ofile.write('VAR\n')
        for (var, type) in variables:
            ofile.write('\t' + var + ': ' + type + ';\n')

        # # write variable assignment declarations
        # ofile.write('ASSIGN\n')
        # for (var, init) in contracts.get_alphabet():
        #     ofile.write('\tinit(' + var + ') := ' + init + ';\n')
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
                    results.append(True)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are satisfiabiles")
                elif check_type == 'compatibility':
                    results.append(True)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are compatible")
                elif check_type == 'consistency':
                    results.append(True)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are consistent")
                elif check_type == 'inclusion':
                    results.append(False)
                    print(str(checks.checks[result_num].aprop) + " is NOT included in " +
                          str(checks.checks[result_num].bprop))
            elif 'is true' in line:
                result_num += 1
                if check_type == 'refinement':
                    results.append(True)
                    print(checks.checks[result_num].get_contracts()[0].get_name() +
                          " is a refinement of " + checks.checks[result_num].get_contracts()[1].get_name())
                elif check_type == 'satisfiability':
                    results.append(False)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are NOT satisfiabiles")
                elif check_type == 'compatibility':
                    results.append(False)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are NOT compatible")
                elif check_type == 'consistency':
                    results.append(False)
                    print(str([contract.get_name() for contract in
                               checks.checks[result_num].get_contracts()]) + " are NOT consistent")
                elif check_type == 'inclusion':
                    results.append(True)
                    print(str(checks.checks[result_num].aprop) + " is included in " +
                          str(checks.checks[result_num].bprop))
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
        if checks.checks[x].check_type == 'inclusion':
            print('The inclusion is', results[x])
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
