from src.patterns import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))


def simple_order_visit():
    visit_1 = OrderedVisit("visit1", ("a", "b"))
    print(visit_1)

    check_1 = Checks()
    check_1.add_check(Satisfiability([visit_1]))

    generate(Contracts([visit_1]), check_1, smv_file)

    results = run(smv_file, check_1)

    print(results)



if __name__ == "__main__":
    smv_file = "patterns_smvfile.smv"

    simple_order_visit()


    #
    # seq_visit_1 = OrderedVisit("odervisit", ("a", "d", "e", "f"))
    # glob_avoidance = GlobalAvoidance("avoid", "g")
    #
    # print(seq_visit_1)
    #
    # contract_list = [visit_1, seq_visit_1, glob_avoidance]
    # contracts = Contracts(contract_list)
    #
    # checks = Checks()
    # checks.add_check(Compatibility("composition", contract_list))
    # checks.add_check(Consistency("composition", contract_list))
    #
    # smv_file = "nusmvfile.smv"
    # generate(contracts, checks, smv_file)
    # results = run(smv_file, checks)
    # print(results)
    # if not results[0]:
    #     print("The mission is not compatible, fix the assumptions")
    # if not results[1]:
    #     print("The mission is not consistent")
    # elif results[0] and results[1]:
    #     print("The mission specified is compatible and consistent, composing now..")
    #     mission = composition(contract_list)
    #     print(mission)

