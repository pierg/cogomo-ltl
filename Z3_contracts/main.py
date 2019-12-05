#!/usr/bin/env python
"""Test Library module provides a test suite for LTL contract verifier"""

import os
import sys
from Z3_contracts.src.parser import parse
from Z3_contracts.src.operations import *
from Z3_contracts.src.cgt import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    cgt_dictionary = parse('spec/test_composition.txt')

    for key, value in cgt_dictionary.items():
        print(str(key) + "\n" + str(value) + "____________________________________________________________________\n\n")


    keep_short_distance = conjoin_goals(
        [cgt_dictionary["accelerate_distance"],
         cgt_dictionary["communication_leader"]], "composition_test")

    print(keep_short_distance)
    print("END")


