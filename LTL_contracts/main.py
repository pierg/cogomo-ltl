import os
import sys
from core import parse, generate, run

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    smv_file = 'nusmvfile.smv'

    contracts, checks = parse('spec/robots.txt')

    generate(contracts, checks, smv_file)

    run(smv_file, checks)

