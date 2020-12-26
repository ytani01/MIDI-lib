#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Paper Tape from MIDI

### for detail and simple usage

$ python3 -m pydoc MidiPaperTape.MidiPaperTape


### API

see comment of ``MidiPaperTape`` class


### sample program

$ ./MidiPaperTape.py file.mid

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import copy
from MidiUtil import Parser
from MyLogger import get_logger


class MidiPaperTape:
    """
    Paper Tape from MIDI

    * チャンネルを選択することができる。


    Simple Usage
    ------------
    ============================================================
    from MidiPaperTape import MidiPaperTape

    parser = MidiPaperTape(midi_file)

    midi_data = parser.parse()
    ============================================================

    """
    CHR_ON = ' '
    CHR_OFF = '*'

    CHR_NOW_ON = 'o'
    CHR_NOW_OFF = '='

    __log = get_logger(__name__, False)

    def __init__(self, midi_data, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_data: list of MidiDataEnt
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_data=%s', midi_data)

        self._midi_data = midi_data

        self._data = self.mk_paper_tape(self._midi_data)

    def mk_paper_tape(self, midi_data=None):
        """
        Parameters
        ----------
        midi_data list of MidiDataEnt

        Returns
        -------
        ch_data: {float: str}
            {abs_time: string}
        """
        if midi_data is None:
            midi_data = self._midi_data

        if self._dbg:
            self.__log.debug('midi_data[%s]', len(midi_data))
            for d in midi_data:
                print(d)

        ch_data = {}
        prev_ch_data = [self.CHR_OFF] * Parser.NOTE_N

        for d in midi_data:
            if d.abs_time not in ch_data.keys():
                ch_data[d.abs_time] = copy.deepcopy(prev_ch_data)

            if d.velocity > 0:
                ch_data[d.abs_time][d.note] = self.CHR_NOW_ON
                prev_ch_data[d.note] = self.CHR_ON
            else:
                ch_data[d.abs_time][d.note] = self.CHR_NOW_OFF
                prev_ch_data[d.note] = self.CHR_OFF

        return ch_data

    def get(self, abs_time):
        """
        Parameters
        ----------
        abs_time: float
        """
        self.__log.debug('abs_time=%s', abs_time)

        return self._data[abs_time]

    def print(self):
        """
        """
        print('-' * (8 + 3 + Parser.NOTE_N + 1))

        print('         | ', end='')
        for i in range(Parser.NOTE_N):
            print('%d' % ((i/100) % 10), end='')
        print()

        print('         | ', end='')
        for i in range(Parser.NOTE_N):
            print('%d' % ((i/10) % 10), end='')
        print()

        print('         | ', end='')
        for i in range(Parser.NOTE_N):
            print('%d' % (i % 10), end='')
        print()

        print('-' * (8 + 3 + Parser.NOTE_N + 1))

        for t in sorted(self._data.keys()):
            print('%08.3f, %a' % (t, ''.join(self._data[t])))


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, out_file, channel=[], debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        out_file: str
            file name of output file
        channel: list of int
            MIDI channel
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('out_file=%s', out_file)
        self.__log.debug('channel=%s', channel)

        self._midi_file = midi_file

        if len(out_file) > 0:
            self._out_file = out_file[0]
        else:
            self._out_file = None

        self._channel = channel

        self._parser = Parser(self._midi_file, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        midi_data = self._parser.parse(self._channel)
        paper_tape = MidiPaperTape(midi_data, debug=self._dbg)

        paper_tape.print()

        if self._out_file:
            with open(self._out_file, mode='w') as f:
                f.write('a')

        self.__log.debug('channel_list=%s', self._parser._channel_list)

        self.__log.debug('done')

    def end(self):
        """ Call at the end of program.
        """
        self.__log.debug('doing ..')
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
MidiPaperTape sample program
''')
@click.argument('midi_file', type=click.Path(exists=True))
@click.argument('out_file', type=str, nargs=-1)
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, out_file, channel, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('midi_file=%s', midi_file)
    __log.debug('out_file=%s', out_file)
    __log.debug('channel=%s', channel)

    app = SampleApp(midi_file, out_file, channel, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
