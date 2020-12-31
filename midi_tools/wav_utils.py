#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Wav file utilites
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import numpy
import pygame
import wave
import array
import time
from .MyLogger import get_logger


class Wav:
    """Wav

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
    """
    DEF_SEC = 1.0  # sec
    DEF_RATE = 11025  # Hz
    VOL_MAX = 1.0
    VOL_MIN = 0.0
    DEF_VOL = 0.25

    __log = get_logger(__name__, False)

    def __init__(self, freq, sec=DEF_SEC, rate=DEF_RATE, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('freq,sec,rate=%s', (freq, sec, rate))

        self._freq = freq
        self._sec = sec
        self._rate = rate

        self.wav = self.mk_wav()

    def mk_wav(self):
        """method1

        Parameters
        ----------
        """
        self.__log.debug('')

        # サンプリングする位置(秒)のarray
        sample_sec = numpy.arange(self._rate * self._sec) / self._rate

        # -32767 .. 32767 の sin波
        sin_wave1 = 32767 * numpy.sin(
            2 * numpy.pi * self._freq * sample_sec)

        # [Important!]
        #   区切りのいい波長に切り詰め、プツブツ音を回避
        sin_list1 = list(sin_wave1)

        while sin_list1[-1] < 0:
            sin_list1.pop()

        while sin_list1[-1] > 0:
            sin_list1.pop()

        # int16に変換
        sin_wave2 = numpy.array(sin_list1, dtype=numpy.int16)

        return sin_wave2

    def save(self, outfile):
        """
        outfile: str
        """
        self.__log.debug('outfile=%s', outfile)

        w_write = wave.Wave_write(outfile)
        w_write.setparams((
            1, 2, self._rate, len(self.wav), 'NONE', 'not compressed'))
        w_write.writeframes(array.array('h', self.wav).tobytes())
        w_write.close()

    def play(self, vol=DEF_VOL):
        """
        Parameters
        ----------
        vol: float
        blocking: bool
        """
        self.__log.debug('vol=%s', vol)

        if vol > self.VOL_MAX:
            vol = self.VOL_MAX
            self.__log.warning('fix: vol=%s', vol)

        if vol < self.VOL_MIN:
            vol = self.VOL_MIN
            self.__log.warning('fix: vol=%s', vol)

        snd = pygame.sndarray.make_sound(self.wav)
        maxtime = int(self._sec * 950)

        snd.set_volume(vol)
        snd.play(fade_ms=20, maxtime=maxtime)
        time.sleep(self._sec)
