#!/usr/bin/env python3

import sys
from miditools import *

midi_file = sys.argv[1]
pa = Parser()
pl = Player()

data = pa.parse(midi_file)

pl.play(data)
