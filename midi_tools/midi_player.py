#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI player
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import time
import pygame
from .wav_utils import Wav
from .midi_utils import note2freq
from .MyLogger import get_logger


class Player:
    """
    MIDI parser for Music Box
    """
    DEF_RATE = 11025  # Hz

    SND_MSEC_MAX = 1.20  # msec
    SND_MSEC_MIN = 0.02  # msec
    SND_PLAY_FACTOR = 0.95

    __log = get_logger(__name__, False)

    def __init__(self, rate=DEF_RATE, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('rate=%s', rate)

        self._rate = rate

        pygame.mixer.init(frequency=self._rate, channels=1)

        self._snd = {}

    def snd_key(self, note_data):
        """
        """
        sec = note_data.length()

        if sec > self.SND_MSEC_MAX:
            sec = self.SND_MSEC_MAX

        if sec < self.SND_MSEC_MIN:
            sec = self.SND_MSEC_MIN

        key_sec = '%.2f' % sec
        key = (note_data.note, key_sec)
        return key

    def mk_wav(self, in_data):
        """
        """
        for i, d in enumerate(in_data):
            if d.velocity == 0:
                continue

            key = self.snd_key(d)

            if key in self._snd.keys():
                continue

            freq = note2freq(d.note)
            sec = d.length()

            if sec > self.SND_MSEC_MAX:
                sec = self.SND_MSEC_MAX

            if sec < self.SND_MSEC_MIN:
                sec = self.SND_MSEC_MIN

            self.__log.debug('%s', key)

            wav = Wav(freq, sec, self._rate).wav

            self._snd[key] = pygame.sndarray.make_sound(wav)

        return

    def play_sound(self, note_data):
        """
        """
        key = self.snd_key(note_data)

        snd = self._snd[key]
        vol = note_data.velocity / 128 / 8
        maxtime = int(self.SND_MSEC_MAX * self.SND_PLAY_FACTOR * 1000)

        snd.set_volume(vol)
        snd.play(fade_ms=5, maxtime=maxtime)

    def play(self, parsed_midi) -> None:
        """
        play parsed midi data

        Parameters
        ----------
        parsed_midi: {
            'channel_set': set of int,
            'data': list of NoteInfo
        }
        """
        data = parsed_midi['data']

        abs_time = 0

        self.mk_wav(parsed_midi['data'])

        for i, d in enumerate(data):
            self.__log.debug('(%4d) %s', i, d)

            delay = d.abs_time - abs_time
            self.__log.debug('delay=%s', delay)

            time.sleep(delay)

            abs_time = d.abs_time
            self.__log.debug('abs_time=%s', abs_time)

            if d.velocity == 0:
                continue

            self.play_sound(d)
            print('(%4d) %s' % (i, d))
