#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser for

### for detail and simple usage

$ python3 -m pydoc mu


### API

see comment of ``mu`` class


### sample program

$ ./mu.py file.mid

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from MyLogger import log, get_logger, set_debug


FREQ_BASE = 440
NOTE_BASE = 69
NOTE_N = 128

def note2freq(note):
    """
    MIDI note number to frequency

    Parameters
    ----------
    note: int

    Returns
    -------
    freq: float
    """
    log.debug('note=%s', note)

    freq = FREQ_BASE * 2.0 ** (float(note - NOTE_BASE)/12.0)
    return freq
