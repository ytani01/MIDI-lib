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

import mido
import copy
from midi_utils import note2freq
from MyLogger import log, get_logger, set_debug


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
    end_time: float
        sec >= abs_time > 0
    """
    __log = get_logger(__name__, True)

    def __init__(self, abs_time=None, channel=None, note=None,
                 velocity=None, end_time=None, debug=False):
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('time,ch,note,velo,end=%s',
                         (abs_time, channel, note, velocity,
                          end_time))

        self.abs_time = abs_time
        self.channel = channel
        self.note = note
        self.velocity = velocity
        self.end_time = end_time
        self.wav = None
        self.snd = None

    def __str__(self):
        """
        Returns
        -------
        str_data: str

        """
        str_data = '%08.3f:' % self.abs_time
        str_data += ' channel=%02d, note:%03d, velocity:%03d' % (
            self.channel, self.note, self.velocity)

        if self.end_time is not None and self.end_time != self.abs_time:
            if type(self.end_time) == float:
                str_data += ' ... end:%08.3f' % (self.end_time)
                str_data += ' (%.2f sec)' % (self.length())

        return str_data

    def length(self):
        self.__log.debug('%08.3f, %s, %s',
                         self.abs_time, self.note, self.velocity)
        return self.end_time - self.abs_time


class Parser:
    """
    MIDI parser for Music Box

    * チャンネルを選択することができる。


    Simple Usage
    ------------
    ============================================================
    import mu

    parser = mu.Parser(midi_file)

    midi_data = parser.parse()
    ============================================================

    """
    __log = get_logger(__name__, False)

    def __init__(self, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('')

        self._channel_set = None

    def parse1(self, midi_obj):
        """
        parse MIDI format simply for subsequent parsing step

        Parameters
        ----------
        midi_obj:
            MIDI file obj

        Returns
        -------
        data: list of DataEnt

        """
        self.__log.debug('midi_obj=%s', midi_obj.__dict__)

        merged_tracks = mido.merge_tracks(midi_obj.tracks)

        tpb = midi_obj.ticks_per_beat

        channel_set = set()
        out_data = []
        abs_time = 0
        cur_tempo = None

        for msg in merged_tracks:
            delta_sec = 0
            try:
                if cur_tempo:
                    delta_sec = mido.tick2second(msg.time, tpb, cur_tempo)
            except KeyError:
                pass

            abs_time += delta_sec

            if msg.type == 'set_tempo':
                cur_tempo = msg.tempo
                continue

            if msg.type == 'end_of_track':
                self.__log.debug(msg.__dict__)
                break

            if msg.type == 'note_off':
                data_ent = DataEnt(abs_time, msg.channel, msg.note, 0,
                                   debug=self._dbg)
                out_data.append(data_ent)
                channel_set.add(msg.channel)

            if msg.type == 'note_on':
                data_ent = DataEnt(abs_time, msg.channel, msg.note,
                                   msg.velocity, debug=self._dbg)
                out_data.append(data_ent)
                channel_set.add(msg.channel)

        return (channel_set, out_data)

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
        out_data: list of DataEnt

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

    def set_end_time(self, in_data):
        """
        """
        self.__log.debug('')

        out_data = copy.deepcopy(in_data)
        note_start = {}

        for i, ent in enumerate(out_data):
            key = (ent.channel, ent.note)

            if ent.velocity > 0:
                if key in note_start.keys():
                    note_start[key].append(i)
                else:
                    note_start[key] = [i]

                self.__log.debug('note_start=%s', note_start)
                continue

            # velocity == 0

            ent.end_time = ent.abs_time

            try:
                idx2 = note_start[key].pop(0)
            except KeyError as ex:
                msg = '%s:%s .. ignored' % (type(ex).__name__, ex)
                self.__log.warning(msg)
                continue

            self.__log.debug('%s, %s, %s', key, note_start[key], idx2)

            out_data[idx2].end_time = ent.abs_time

            if not note_start[key]:
                note_start.pop(key)

            self.__log.debug('note_start=%s', note_start)

        for k in note_start:
            for idx in note_start[k]:
                out_data[idx].end_time = ent.abs_time

        self.__log.debug('note_start=%s', note_start)

        return out_data

    def parse(self, midi_file, channel=None):
        """
        parse MIDI data

        Parameters
        ----------
        midi_file: str
            MIDI file name
        channel: list of int or None for all channels
            MIDI channel

        Returns
        -------
        out_data: {'channel_set': list of int, 'data': list of DataEnt}

        """
        self.__log.debug('midi_file=%s, channel=%s', midi_file, channel)

        midi_obj = mido.MidiFile(midi_file)

        self._channel_set, data1 = self.parse1(midi_obj)

        if self._dbg:
            self.__log.debug('data1=')
            for d in data1:
                print(d)
        self.__log.debug('channel_set=%s', self._channel_set)

        data2 = self.select_channel(data1, channel)

        data3 = self.set_end_time(data2)

        out_data = {'channel_set': self._channel_set, 'data': data3}
        return out_data


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
        self._channel = channel

        if len(out_file) > 0:
            self._out_file = out_file[0]
        else:
            self._out_file = None

        self._parser = Parser(debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        parsed_data = self._parser.parse(self._midi_file, self._channel)

        interval = []

        print('parsed data ..')
        for i, d in enumerate(parsed_data['data']):

            if d.length() > 0:
                interval.append(round(d.length(), 3))

            if d.velocity == 0:
                continue

            print('(%4d) %s' % (i, d))

        print('channel_set=%s' % (parsed_data['channel_set']))
        interval = sorted(list(set(interval)))

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
@click.option('--debug', '-d', 'dbg', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, out_file, channel, dbg):
    """サンプル起動用メイン関数
    """
    set_debug(dbg)
    log.debug('midi_file=%s', midi_file)
    log.debug('out_file=%s', out_file)
    log.debug('channel=%s', channel)

    app = SampleApp(midi_file, out_file, channel, debug=dbg)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
