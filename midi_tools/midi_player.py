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
    DEF_RATE = 11025  # Hz .. sampling rate

    SEC_MIN = 0.02  # sec
    SEC_MAX = 1.20  # sec

    # SND_PLAY_FACTOR = 0.95 * 1000

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

        self._sec_min = self.SEC_MIN
        self._sec_max = self.SEC_MAX

        pygame.mixer.init(frequency=self._rate, channels=1)

        self._snd = {}

    @staticmethod
    def within_range(n, n_min, n_max):
        """
        keep n within range
        """
        return min(max(n, n_min), n_max)

    def snd_key(self, note_data, sec_min, sec_max):
        """
        """
        sec = self.within_range(note_data.length(), sec_min, sec_max)

        if sec > 0.5:
            # 0.02 単位に丸める
            key_sec = round(round(sec / 2.0, 2) * 2, 2)
        else:
            key_sec = round(sec, 2)

        key = (note_data.note, key_sec)
        return key

    def mk_wav(self, in_data, sec_min, sec_max):
        """
        """
        for i, d in enumerate(in_data):
            if d.velocity == 0:
                continue

            key = self.snd_key(d, sec_min, sec_max)

            if key in self._snd.keys():
                continue

            self.__log.debug('new key: %s', key)

            freq = note2freq(d.note)
            sec = self.within_range(d.length(), sec_min, sec_max)

            wav = Wav(freq, sec, self._rate).wav

            self._snd[key] = pygame.sndarray.make_sound(wav)

        return self._snd

    def play_sound(self, note_data, sec_min, sec_max) -> None:
        """
        """
        key = self.snd_key(note_data, sec_min, sec_max)

        snd = self._snd[key]
        vol = note_data.velocity / 128 / 8
        # maxtime = int(sec_max * self.SND_PLAY_FACTOR)

        snd.set_volume(vol)
        # snd.play(fade_ms=5, maxtime=maxtime)
        snd.play()

    def play(self, parsed_midi, sec_min=SEC_MIN, sec_max=SEC_MAX) -> None:
        """
        play parsed midi data

        Parameters
        ----------
        parsed_midi: {'channel_set': set of int, 'data': list of NoteInfo}
        sec_min: int
            min sound length
        sec_max: int
            max sound length
        """
        self.__log.debug('parsed_midi[channel_set]=%s,',
                         parsed_midi['channel_set'])
        self.__log.debug('length of parsed_midi[data]=%s',
                         len(parsed_midi['data']))
        self.__log.debug('sec: %s .. %s', sec_min, sec_max)

        data = parsed_midi['data']

        snd = self.mk_wav(parsed_midi['data'], sec_min, sec_max)
        self.__log.info('len(snd)=%s', len(snd))

        abs_time = 0

        for i, d in enumerate(data):
            self.__log.debug('(%4d) %s', i, d)

            delay = d.abs_time - abs_time
            self.__log.debug('delay=%s', delay)

            if delay > 0:
                time.sleep(delay)

            abs_time = d.abs_time
            self.__log.debug('abs_time=%s', abs_time)

            if d.velocity == 0:
                continue

            self.play_sound(d, sec_min, sec_max)
            print('(%4d) %s' % (i, d))

        time.sleep(.5)
