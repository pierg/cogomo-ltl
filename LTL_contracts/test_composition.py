from src.patterns import *
from src.context import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))



class Incompatible(Exception):
    print("Incompatible Exception")

class Inconsistent(Exception):
    print("Inconsistency Exception")

class Unsatisfiable(Exception):
    print("Unsatisfiable Exception")



def check_satisfiability(contract):
    """

    :param contract:
    :return:
    """
    checks = Checks()

    checks.add_check(Satisfiability([contract]))
    generate(Contracts([contract]), checks, smv_file)

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

    generate(Contracts(list_contracts), checks, smv_file)
    results = run(smv_file, checks)

    if not results[0]:
        print("The contracts are not compatible, fix the assumptions")
        raise Incompatible
    if not results[1]:
        print("The contracts are not consistent")
        raise Inconsistent
    elif results[0] and results[1]:
        print("The contracts are compatible and consistent")



if __name__ == "__main__":
    smv_file = "test_smvfile.smv"

    robot_1 = Robot("robot_1", "M")
    robot_1.add_assumption("G(N)")
    robot_2 = Robot("robot_2", "N")


    composed = composition([robot_1, robot_2])

    print("COMPOSED \n" + str(composed))
