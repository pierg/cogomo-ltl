import os
import sys
from core import parse, generate, run
from operations import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    smv_file = 'nusmvfile.smv'

    contracts, checks = parse('spec/test.txt')

    generate(contracts, checks, smv_file)

    run(smv_file, checks)

    composed_contracts = composition(contracts.contracts.values())

    print(composed_contracts)

