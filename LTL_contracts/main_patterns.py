from src.patterns import *
from src.context import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":
    # simple_order_visit_example()
    # visit_with_conflict_example()

    """ The designer specifies the mission """
    visit_locations = OrderedVisit("visit_locations_A_B", ("locA", "locB"))
    pickup_object = DelayedReaction("pickup_HI_when_in_A", "locA", "HI_pickup")

    """ Adding contextual assumptions relative to location and the lifting the weight """
    visit_locations.add_physical_assumptions()
    pickup_object.add_variable(("weight_power", "5..15"))
    pickup_object.add_assumption("G (weight_power > 10)")

    mission = [visit_locations, pickup_object]

    for contract in mission:
        check_satisfiability(contract)

    check_compatibility_consistency(mission)

    mission_composed = composition(mission)

    check_satisfiability(mission_composed)

    print("COMPOSED MISSION\n" + str(mission_composed))

    """ Istanciate it in a context """
    robot_1 = Robot("robot_1", "weight_power > 5 & weight_power < 10")

    mission.append(robot_1)

    check_compatibility_consistency(mission)

    mission_composed_2 = composition(mission)

    print("COMPOSED MISSION WITH ROBOT\n" + str(mission_composed_2))
