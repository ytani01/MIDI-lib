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
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)

        self._midi_file = midi_file
        self._midi = mido.MidiFile(self._midi_file)
        self.__log.debug('ticks_per_beet=%s', self._midi.ticks_per_beat)

    def parse0(self, midi_data):
        """
        parse MIDI format simply for subsequent parsing step

        Parameters
        ----------
        midi_data:
            MIDI data

        Returns
        -------
        data: list of data_ent
            data_ent: ex.
            {'midi_track': 3, 'midi_channecl': 5, 'note': 65,
             'abs_time': 500, 'delay': 300}

        """
        self.__log.debug('midi_data=%s', midi_data.__dict__)

        abs_time = 0

        cur_tempo = None
        cur_track = None
        cur_channel = None

        data = []

        abs_time = 0
        for i, track in enumerate(midi_data.tracks):
            cur_track = i
            abs_time = 0
            
            for msg in track:
                try:
                    abs_time += msg.time
                except KeyError:
                    pass

                try:
                    if msg.channel != cur_channel:
                        cur_channel = msg.channel
                        self.__log.debug('cur_channel=%d', cur_channel)
                except AttributeError:
                    pass

                if msg.type == 'end_of_track':
                    continue

                if msg.type == 'note_on':
                    data_ent= {
                        'abs_time': abs_time,
                        'track': cur_track,
                        'channel': cur_channel, 
                        'note': msg.note,
                        'velocity': msg.velocity,
                        'time': msg.time
                    }
                    self.__log.debug('data_ent=%s', data_ent)

                    data.append(data_ent)

                    continue

                if msg.type == 'set_tempo':
                    cur_tempo = msg.tempo
                    continue

                self.__log.debug('abs_time=%d, msg=%s',
                                 abs_time, msg.__dict__)

        merged_tracks=mido.merge_tracks(midi_data.tracks)
        abs_time = 0
        
        for msg in merged_tracks:
            try:
                abs_time += msg.time
            except KeyError:
                pass

            if msg.type == 'end_of_track':
                continue

            if msg.type == 'note_on':
                data_ent= {
                    'abs_time': abs_time,
                    'channel': msg.channel,
                    'note': msg.note,
                    'velocity': msg.velocity,
                    'time': msg.time
                }
                self.__log.debug('data_ent=%s', data_ent)

                data.append(data_ent)

                continue

            self.__log.debug('abs_time=%d, msg=%s',
                             abs_time, msg.__dict__)

        return data

    def mix_track_channecl(self, data):
        """
        複数トラック/チャンネルを重ね合わせる

        Parameters
        ----------
        data: list of data_ent

        Returns
        -------
        mixed_data: list of data_ent

        """
        # self.__log.debug('data=%s', data)

        if len(data) == 0:
            return []

        mixed_data = sorted(data, key=operator.itemgetter('abs_time'))

        d0 = mixed_data.pop(0)
        prev_d = d0

        for d in mixed_data:
            delay = d['abs_time'] - prev_d['abs_time']
            prev_d['delay'] = delay
            prev_d = d

        mixed_data.insert(0, d0)
        return mixed_data

    def select_track_channel(self, data0, track=[], channel=[]):
        """
        指定されたトラック/チャンネルだけを抽出

        Parameters
        ----------
        data0: list of data_ent

        track: list of int
            MIDI track
        channel: list of int
            MIDI channel

        Returns
        -------
        data1: list of data_ent

        """
        self.__log.debug('track=%s, channel=%s', track, channel)

        data1 = []

        for d in data0:
            if len(track) == 0 and len(channel) == 0:
                data1.append(d)
                continue

            if len(track) == 0 and len(channel) > 0:
                if d['midi_channel'] in channel:
                    data1.append(d)
                    continue

            if len(track) > 0 and len(channel) == 0:
                if d['midi_track'] in track:
                    data1.append(d)
                    continue

            if d['midi_track'] in track and d['midi_channel'] in channel:
                data1.append(d)

        return data1

    def parse(self, track=None, channel=None):
        """
        parse MIDI data

        base が None の場合は、最適値を自動選択する。

        Parameters
        ----------
        track: list of int or None for all tracks
            MIDI track
        channel: list of int or None for all channels
            MIDI channel

        Returns
        -------
        midi_data: list of midi_ent

        """
        self.__log.debug('track=%s, channel=%s',
                         track, channel)

        # 1st step of parsing
        midi_data0 = self.parse0(self._midi)

        return midi_data0

        midi_track_channel = []
        for i, d in enumerate(midi_data0):
            midi_track_channel.append(
                (d['midi_track'], d['midi_channel']))
            midi_track_channel = sorted(list(set(midi_track_channel)))

        self.__log.debug('midi_track_channel=%s', midi_track_channel)

        # select MIDI track/channel
        midi_data1 = self.select_track_channel(midi_data0, track, channel)
        for i, d in enumerate(midi_data1):
            self.__log.debug('%s: %s', i, d)

        return midi_data0


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, out_file, track=[], channel=[],
                 debug=False):
        """constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        out_file: str
            file name of output file
        track: list of int
            MIDI track
        channel: list of int
            MIDI channel
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('out_file=%s', out_file)
        self.__log.debug('track=%s, channel=%s', track, channel)

        self._midi_file = midi_file

        if len(out_file) > 0:
            self._out_file = out_file[0]
        else:
            self._out_file = None

        self._track = track
        self._channel = channel

        self._parser = MidiParser(self._midi_file, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        midi_data = self._parser.parse(self._track, self._channel)

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
@click.option('--track', '-t', 'track', type=int, multiple=True,
              help='MIDI track')
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, out_file, track, channel, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('midi_file=%s', midi_file)
    __log.debug('out_file=%s', out_file)
    __log.debug('track=%s, channel=%s', track, channel)

    app = SampleApp(midi_file, out_file, track, channel, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
