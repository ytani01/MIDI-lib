#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2020'

import copy
import mido
from .MyLogger import get_logger


class NoteInfo:
    """
    parsed MIDI data entity

    Attributes
    ----------
    abs_time: float
        sec >= 0
    channel: int
        0 .. 15
    note: int
        0 .. 127
    velocity: int
        0 .. 127
    end_time: float
        sec >= abs_time >= 0
    """
    __log = get_logger(__name__, True)

    def __init__(self,  # pylint: disable=too-many-arguments
                 abs_time=None, channel=None, note=None,
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
            if isinstance(self.end_time, float):
                str_data += ' ... end:%08.3f' % (self.end_time)
                str_data += ' (%.2f sec)' % (self.length())

        return str_data

    def length(self):
        """
        Returns
        -------
        length: float
            length of note [msec]
        """
        return self.end_time - self.abs_time


class Parser:
    """
    MIDI parser
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
        data: list of NoteInfo

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
                data_ent = NoteInfo(abs_time, msg.channel, msg.note, 0,
                                    debug=self._dbg)
                out_data.append(data_ent)
                channel_set.add(msg.channel)

            if msg.type == 'note_on':
                data_ent = NoteInfo(abs_time, msg.channel, msg.note,
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
        out_data: list of NoteInfo

        """
        self.__log.debug('channel=%s', channel)

        if channel is None or not channel:
            out_data = copy.deepcopy(in_data)
            return out_data

        out_data = []
        for data in in_data:
            if data.channel in channel:
                out_data.append(data)

        return out_data

    def set_end_time(self, in_data):
        """
        set end time of NoteInfo
        """
        self.__log.debug('')

        out_data = copy.deepcopy(in_data)
        note_start = {}

        ent = None
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
                if ent:
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
        out_data: {
            'channel_set': set of int,
            'data': list of NoteInfo
        }

        """
        self.__log.debug('midi_file=%s, channel=%s', midi_file, channel)

        midi_obj = mido.MidiFile(midi_file)

        self._channel_set, data1 = self.parse1(midi_obj)

        if self._dbg:
            self.__log.debug('data1=')
            for data in data1:
                print(data)

        self.__log.debug('channel_set=%s', self._channel_set)

        data2 = self.select_channel(data1, channel)

        data3 = self.set_end_time(data2)

        out_data = {'channel_set': self._channel_set, 'data': data3}
        return out_data
