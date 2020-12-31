#!/usr/bin/env python3

import sys
from midi_tools import *

pa = Parser()
pl = Player()

data = pa.parse(sys.argv[1])
pl.play(data)
