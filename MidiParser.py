#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser for

### for detail and simple usage

$ python3 -m pydoc MidiParser.MidiParser


### API

see comment of ``MidiParser`` class


### sample program

$ ./MidiParser.py file.mid

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import mido
import json
import operator
import copy
from MyLogger import get_logger


class MidiParser:
    """
    MIDI parser for Music Box

    * トラック/チャンネルを選択することができる。


    Simple Usage
    ------------
    ============================================================
    from MidiParser import MidiParser

    parser = MidiParser(midi_file)

    midi_data = parser.parse()
    ============================================================

    """
    NOTE_N = 128
    DEF_NOTE_BASE = 60

    CHR_ON = ' '
    CHR_OFF = '*'

    CHR_NOW_ON = 'o'
    CHR_NOW_OFF = '='

    __log = get_logger(__name__, False)

    def __init__(self, midi_file, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)

        self._midi_file = midi_file

        self._midi = mido.MidiFile(self._midi_file)

        self._tpb =  self._midi.ticks_per_beat
        self._channel_list = []

    def parse1(self, midi_data):
        """
        parse MIDI format simply for subsequent parsing step

        Parameters
        ----------
        midi_data:
            MIDI data

        Returns
        -------
        data: list of data_ent
            data_ent_ex = {
              'abs_data': 930,
              'midi_channecl': 5,
              'note': 65,
              'time': 300
            }

        """
        self.__log.debug('midi_data=%s', midi_data.__dict__)

        out_data = []

        merged_tracks=mido.merge_tracks(midi_data.tracks)
        abs_time = 0
        self._channel_list = []
        cur_tempo = None

        for msg in merged_tracks:
            delta_sec = 0
            try:
                if cur_tempo:
                    delta_sec = mido.tick2second(msg.time, self._tpb,
                                                 cur_tempo)
            except KeyError:
                pass

            abs_time += delta_sec

            if msg.type == 'end_of_track':
                continue

            if msg.type == 'set_tempo':
                cur_tempo = msg.tempo
                continue

            if msg.type == 'note_off':
                data_ent = {
                    'abs_time': abs_time,
                    'channel': msg.channel,
                    'note': msg.note,
                    'velocity': 0,
                    'delta': delta_sec
                }
                out_data.append(data_ent)
                self._channel_list.append(msg.channel)

            if msg.type == 'note_on':
                data_ent = {
                    'abs_time': abs_time,
                    'channel': msg.channel,
                    'note': msg.note,
                    'velocity': msg.velocity,
                    'delta': delta_sec
                }
                out_data.append(data_ent)
                self._channel_list.append(msg.channel)

        self._channel_list = sorted(list(set(self._channel_list)))

        return out_data

    def select_channel(self, in_data, channel=None):
        """
        指定されたトラック/チャンネルだけを抽出

        Parameters
        ----------
        in_data: list of data_ent

        channel: list of int
            MIDI channel

        Returns
        -------
        out_data: list of data_ent

        """
        self.__log.debug('channel=%s', channel)

        if channel is None or len(channel) == 0:
            out_data = copy.deepcopy(in_data)
            return out_data

        out_data = []
        for d in in_data:
            if d['channel'] in channel:
                out_data.append(d)

        return out_data

    def parse2(self, in_data):
        """
        """
        n_list = {}
        prev_n_list = [self.CHR_OFF] * self.NOTE_N
        for d in in_data:
            abs_time = d['abs_time']
            note = d['note']
            velocity = d['velocity']

            if abs_time not in n_list.keys():
                n_list[abs_time] = copy.deepcopy(prev_n_list)

            if velocity > 0:
                n_list[abs_time][note] = self.CHR_NOW_ON
                prev_n_list[note] = self.CHR_ON
            else:
                n_list[abs_time][note] = self.CHR_NOW_OFF
                prev_n_list[note] = self.CHR_OFF

        return n_list

    def parse(self, channel=None):
        """
        parse MIDI data

        Parameters
        ----------
        channel: list of int or None for all channels
            MIDI channel

        Returns
        -------
        midi_data: list of midi_ent

        """
        self.__log.debug('channel=%s', channel)

        data1 = self.parse1(self._midi)

        for d in data1:
            msg = '%08.3f' % d['abs_time']
            msg += ',ch:%02d' % d['channel']
            msg += ',note:%03d' % d['note']
            msg += ',velocity:%03d' % d['velocity']
            msg += ',delta:%06.3f' % d['delta']
            self.__log.debug(msg)

        data1a = self.select_channel(data1, channel)

        data2 = self.parse2(data1a)

        return data2


    def print_data2(self, data2):
        """
        """
        print('           ', end='')
        for i in range(self.NOTE_N):
            print('%d' % ((i/100) % 10), end='')
        print()

        print('           ', end='')
        for i in range(self.NOTE_N):
            print('%d' % ((i/10) % 10), end='')
        print()

        print('           ', end='')
        for i in range(self.NOTE_N):
            print('%d' % (i % 10), end='')
        print()

        for t in data2.keys():
            print('%08.3f, %a' % (t, ''.join(data2[t])))


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, out_file, channel=[], debug=False):
        """constructor

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

        self._parser = MidiParser(self._midi_file, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        midi_data = self._parser.parse(self._channel)
        self._parser.print_data2(midi_data)

        self.__log.debug('channel_list=%s', self._parser._channel_list)

        if self._out_file:
            with open(self._out_file, mode='w') as f:
                f.write('a')

        self.__log.debug('done')

    def end(self):
        """ Call at the end of program.
        """
        self.__log.debug('doing ..')
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
MidiParser sample program
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
