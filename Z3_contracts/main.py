#!/usr/bin/env python
"""Test Library module provides a test suite for LTL contract verifier"""

import os
import sys
from Z3_contracts.src.parser import parse
from Z3_contracts.src.operations import *
from Z3_contracts.src.cgt import *

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))

if __name__ == "__main__":

    """Parse Goals from Structured Text File"""
    goals = parse('spec/platooning.txt')

    """Declare New Goals that are built on top of existing goals"""
    keep_short_distance = conjoin_goals(
        [goals["accelerate_distance"], goals["decelerate_distance"], goals["maintainspeed_distance"]],
        "keep_short_distance",
        "keep a short distance from the vehicle ahead")

    follow_leader = conjoin_goals(
        [goals["accelerate_follow"], goals["decelerate_follow"], goals["maintainspeed_follow"]],
        "follow_leader",
        "follow the leader vehicle by keeping its speed")




    print("END")


