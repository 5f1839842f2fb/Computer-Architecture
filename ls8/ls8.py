#!/usr/bin/env python3
import sys

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) != 2:
    print("Exactly one additional argument please")
    sys.exit()

cpu.load(sys.argv[1])
cpu.run()