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
import time
import threading
import pygame
from WavUtil import Wav
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
                str_data += ' (%.3f sec)' % (self.length())

        return str_data

    def length(self):
        return self.end_time - self.abs_time


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

        self._channel_list = None

        self._mu = Util(debug=self._dbg)

        pygame.mixer.init(channels=1)

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
        out_data = []
        abs_time = 0
        self._channel_list = []
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
            if ent.velocity > 0:
                note_start[(ent.channel, ent.note)] = i
                self.__log.debug('note_start=%s', note_start)
                continue

            # velocity == 0

            ent.end_time = ent.abs_time

            try:
                i2 = note_start[(ent.channel, ent.note)]
            except KeyError as ex:
                msg = '%s:%s' % (type(ex).__name__, ex)
                self.__log.warning(msg)
                continue

            if i2 is None:
                continue

            out_data[i2].end_time = ent.abs_time

            note_start[(ent.channel, ent.note)] = None

        self.__log.debug('note_start=%s', note_start)

        for k in note_start.keys():
            if note_start[k] is not None:
                i2 = note_start[k]
                out_data[i2].end_time = ent.abs_time
                note_start[k] = None

        self.__log.debug('note_start=%s', note_start)

        return out_data

    def mk_wav(self, in_data):
        """
        """
        rate = 44100

        for i, d in enumerate(in_data):
            print(i, d)
            if d.velocity == 0:
                continue

            freq = self._mu.note2freq(d.note)

            wav = Wav(freq, d.length(), rate, debug=self._dbg)._wav

            d.snd = pygame.sndarray.make_sound(wav)
            d.snd.set_volume(d.velocity/128/8)

        return in_data

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
        out_data: {'channel_list': list of int, 'data': list of DataEnt}

        """
        self.__log.debug('midi_file=%s, channel=%s', midi_file, channel)

        midi_obj = mido.MidiFile(midi_file)

        data1 = self.parse1(midi_obj)

        if self._dbg:
            self.__log.debug('data1=')
            for d in data1:
                print(d)

        data2 = self.select_channel(data1, channel)

        data3 = self.set_end_time(data2)

        data4 = self.mk_wav(data3)

        out_data = {'channel_list': self._channel_list, 'data': data4}
        return out_data

    def play_sound(self, data):
        """
        must be override
        """
        data.snd.play(fade_ms=50)

    def play(self, parsed_midi):
        """
        """
        channel_list = parsed_midi['channel_list']
        data = parsed_midi['data']

        abs_time = 0

        for i, d in enumerate(data):
            self.__log.debug('(%4d) %s', i, d)

            delay = d.abs_time - abs_time
            self.__log.debug('delay=%s', delay)

            time.sleep(delay)

            abs_time = d.abs_time
            self.__log.debug('abs_time=%s', abs_time)

            if d.channel not in channel_list:
                continue

            if d.velocity == 0:
                continue

            self.play_sound(d)
#            threading.Thread(target=self.play_sound, args=(d,),
#                             daemon=True).start()


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, out_file, channel=[],
                 note_end_flag=False, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        out_file: str
            file name of output file
        channel: list of int
            MIDI channel
        note_end_flag: bool

        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('out_file=%s', out_file)
        self.__log.debug('channel=%s', channel)
        self.__log.debug('note_end_flag=%s', note_end_flag)

        self._midi_file = midi_file
        self._channel = channel
        self._note_end_flag = note_end_flag

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

            if d.velocity == 0 and self._note_end_flag is False:
                continue

            print('(%4d) %s' % (i, d))

        print('channel_list=%s' % (parsed_data['channel_list']))
        interval = sorted(list(set(interval)))
        print('interval=%s' % (interval))

        self._parser.play(parsed_data)

        if self._out_file:
            with open(self._out_file, mode='w') as f:
                # TBD
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
@click.option('--note_end', '-e', 'note_end', is_flag=True,
              default=False,
              help="print note end flag")
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, out_file, channel, note_end, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('midi_file=%s', midi_file)
    __log.debug('out_file=%s', out_file)
    __log.debug('channel=%s', channel)
    __log.debug('note_end=%s', note_end)

    app = SampleApp(midi_file, out_file, channel, note_end, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
