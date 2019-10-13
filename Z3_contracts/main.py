#!/usr/bin/env python
"""Test Library module provides a test suite for LTL contract verifier"""

import os
import sys
from Z3_contracts.src.parser import parse
from Z3_contracts.src.operations import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    cgt, contracts, checks = parse('spec/test.txt')

    print(contracts)

    composed_contracts = composition(contracts)

    print(composed_contracts)



