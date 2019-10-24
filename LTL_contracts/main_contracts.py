import os
import sys
from core import parse, generate, run
from operations import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    smv_file = 'nusmvfile.smv'

    contracts, checks = parse('spec/test_2.txt')

    for contract in contracts.get_contracts():
        print(contract)

    generate(contracts, checks, smv_file)

    results = run(smv_file, checks)

    print("Check results:" + str(results))