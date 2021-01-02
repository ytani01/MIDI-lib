#!/usr/bin/env python3

import sys
from midilib import *

midi_file = sys.argv[1]
pa = Parser()
pl = Player()

parsed_data = pa.parse(midi_file)

pl.play(parsed_data)
