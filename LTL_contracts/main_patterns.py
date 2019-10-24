from src.patterns import *
from src.context import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))



class Incompatible(Exception):
    print("Incompatible Exception")

class Inconsistent(Exception):
    print("Inconsistency Exception")

class Unsatisfiable(Exception):
    print("Unsatisfiable Exception")



def simple_order_visit_example():
    visit_1 = OrderedVisit("visit1", ("a", "a", "c", "d"))

    print(visit_1)

    # It adds that the robot cannot be in the same location at the same time
    visit_1.add_physical_assumptions()

    print(visit_1)

    check_1 = Checks()

    check_1.add_check(Satisfiability([visit_1]))

    generate(Contracts([visit_1]), check_1, smv_file)

    results = run(smv_file, check_1)

    print(results)


def visit_with_conflict_example():
    ordered_visit = OrderedVisit("odervisit", ("a", "b"))

    glob_avoidance = GlobalAvoidance("avoid", "b")

    contract_list = [ordered_visit, glob_avoidance]
    contracts = Contracts(contract_list)

    checks = Checks()
    checks.add_check(Compatibility("composition", contract_list))
    checks.add_check(Consistency("composition", contract_list))

    generate(contracts, checks, smv_file)
    results = run(smv_file, checks)

    print(results)
    if not results[0]:
        print("The mission is not compatible, fix the assumptions")
    if not results[1]:
        print("The mission is not consistent")
    elif results[0] and results[1]:
        print("The mission specified is compatible and consistent, composing now..")
        mission = composition(contract_list)
        print(mission)


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
    smv_file = "patterns_smvfile.smv"
    # simple_order_visit_example()
    # visit_with_conflict_example()

    """ The designer specifies the mission """
    visit_locations = OrderedVisit("visit_locations_A_B", ("locA", "locB"))
    pickup_object = DelayedReaction("pickup_HI_when_in_A", "locA", "HI_pickup")

    """ Adding contextual assumptions relative to location and the lifting the weight """
    visit_locations.add_physical_assumptions()
    pickup_object.add_variable(("powerGreaterThanX", "boolean"))
    pickup_object.add_assumption("powerGreaterThanX")

    mission = [visit_locations, pickup_object]

    for contract in mission:
        check_satisfiability(contract)

    check_compatibility_consistency(mission)

    mission_composed = composition(mission)

    check_satisfiability(mission_composed)

    print("COMPOSED MISSION\n" + str(mission_composed))

    """ Istanciate it in a context """
    robot_1 = Robot("robot_1", "powerGreaterThanX")

    mission.append(robot_1)

    mission_composed_2 = composition(mission)

    print("COMPOSED MISSION WITH ROBOT\n" + str(mission_composed_2))
