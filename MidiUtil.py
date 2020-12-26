#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser for

### for detail and simple usage

$ python3 -m pydoc MidiUtil


### API

see comment of ``MidiUtil`` class


### sample program

$ ./MidiUtil.py file.mid

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import mido
import copy
from MyLogger import get_logger


__log = get_logger(__name__, False)


class Util:
    """
    MIDI Utilties
    """
    __log = get_logger(__name__, True)

    FREQ_BASE = 440
    NOTE_BASE = 69

    NOTE_MIN = 41   # ?
    NOTE_MAX = 112  # ?

    def __init__(self, debug=False):
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)

    def note2freq(self, note):
        """
        MIDI note number to frequency

        Parameters
        ----------
        note: int

        Returns
        -------
        freq: float
        """
        self.__log.debug('note=%s', note)

        freq = self.FREQ_BASE * 2.0 ** (float(note - self.NOTE_BASE)/12.0)
        return freq


class DataEnt:
    """
    MIDI data entry

    Attributes
    ----------
    abs_time: float
        sec > 0
    channel: int
        0 .. 15
    note: int
        0 .. 127
    velocity: int
        0 .. 127
    """
    __log = get_logger(__name__, True)

    def __init__(self, abs_time=None, channel=None, note=None,
                 velocity=None, debug=False):
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('time,ch,note,velo=%s',
                         (abs_time, channel, note, velocity))

        self.abs_time = abs_time
        self.channel = channel
        self.note = note
        self.velocity = velocity

    def __str__(self):
        return '%08.3f, ch:%02d, note:%03d, velocity:%03d' % (
            self.abs_time, self.channel, self.note, self.velocity)


class Parser:
    """
    MIDI parser for Music Box

    * チャンネルを選択することができる。


    Simple Usage
    ------------
    ============================================================
    import MidiUtil

    parser = MidiUtil.Parser(midi_file)

    midi_data = parser.parse()
    ============================================================

    """
    NOTE_N = 128
    DEF_NOTE_BASE = 60

    __log = get_logger(__name__, False)

    def __init__(self, midi_file, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)

        self._midi_file = midi_file

        self._midi = mido.MidiFile(self._midi_file)

        self._tpb = self._midi.ticks_per_beat
        self._channel_list = []

    def parse1(self, midi_file_obj):
        """
        parse MIDI format simply for subsequent parsing step

        Parameters
        ----------
        midi_file_obj:
            MIDI file obj

        Returns
        -------
        data: list of DataEnt
        """
        self.__log.debug('midi_file_obj=%s', midi_file_obj.__dict__)

        out_data = []

        merged_tracks = mido.merge_tracks(midi_file_obj.tracks)
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
                data_ent = DataEnt(abs_time, msg.channel, msg.note, 0,
                                   debug=self._dbg)
                out_data.append(data_ent)
                self._channel_list.append(msg.channel)

            if msg.type == 'note_on':
                data_ent = DataEnt(abs_time, msg.channel, msg.note,
                                   msg.velocity, debug=self._dbg)
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
            if d.channel in channel:
                out_data.append(d)

        return out_data

    def parse(self, channel=None):
        """
        parse MIDI data

        Parameters
        ----------
        channel: list of int or None for all channels
            MIDI channel

        Returns
        -------
        midi_data: list of DataEnt
        """
        self.__log.debug('channel=%s', channel)

        data1 = self.parse1(self._midi)

        if self._dbg:
            self.__log.debug('data1=')
            for d in data1:
                print(d)

        data1a = self.select_channel(data1, channel)

        if self._dbg:
            self.__log.debug('data1a=')
            for d in data1a:
                print(d)

        return data1a


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
        for d in midi_data:
            print(d)

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
MidiUtil sample program
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
