from src.patterns import *
from src.context import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))



def simple_order_visit_example():
    visit_1 = OrderedVisit("visit1", ("a", "a", "c", "d"))

    print(visit_1)

    # It adds that the robot cannot be in the same location at the same time
    visit_1.add_physical_assumptions()

    print(visit_1)

    check_1 = Checks()

    check_1.add_check(Satisfiability([visit_1]))

    generate(Contracts([visit_1]).get_alphabet(), check_1, smv_file)

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


def check_inclusion_test_example():

    pickup_object = DelayedReaction("pickup_HI_when_in_A", "locA", "HI_pickup")

    pickup_object.add_assumption("G(weight_power > 10)")

    print(pickup_object)

    robot_1 = Robot("robot_1", "G(weight_power > 10)")

    print(robot_1)

    mission = [pickup_object, robot_1]

    mission_composed = composition(mission)

    print("MISSION\n" + str(mission_composed))

    mission_composed_simplify = composition_simplify(mission)

    print("\nMISSION SIMPLIFIED\n" + str(mission_composed_simplify))


if __name__ == "__main__":
    # simple_order_visit_example()
    # visit_with_conflict_example()

    check_inclusion_test_example()