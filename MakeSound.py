#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Make sound

### Install

(1) Linux packages

$ apt install portaudio2

(2) Python packages

$ pip install -U numpy sounddevice

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import numpy
import sounddevice
import time
from MyLogger import get_logger


class MakeSound:
    """MakeSound

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
    """
    DEF_TIME = 2.0  # sec
    DEF_RATE = 44100  # Hz
    VOL_MAX = 20000
    DEF_VOL = 10000

    __log = get_logger(__name__, False)

    def __init__(self, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('')

    def end(self):
        """end

        Call at the end of program
        """
        self.__log.debug('doing ..')
        print('end of MakeSound')
        self.__log.debug('done')

    def mk_wav(self, freq, vol=10000, time=DEF_TIME, rate=DEF_RATE):
        """method1

        Parameters
        ----------
        """
        self.__log.debug('freq,time,rate=%s', (freq, time, rate))

        samples = numpy.arange(rate * time) / rate
        wave = vol * numpy.sin(2 * numpy.pi * freq * samples)
        wav_wave = numpy.array(wave, dtype=numpy.int16)

        self.__log.debug('wav_wave=%s', wav_wave)
        return wav_wave

    def play_wav(self, wav_wave, rate=DEF_RATE, blocking=True):
        """
        """
        self.__log.debug('wav_wave=%s, blocking=%s', wav_wave, blocking)

        sounddevice.default.samplerate = rate
        sounddevice.play(wav_wave, blocking=blocking)


# --- 以下、サンプル ---


class SampleApp:
    """Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, freq, vol, time, rate, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('freq,time,rate=%s', (freq, time, rate))

        self._freq = freq
        self._vol = vol
        self._time = time
        self._rate = rate

        self._mk_sound = MakeSound(debug=self._dbg)

    def main(self):
        """main
        """
        self.__log.debug('')

        wav_wave1 = self._mk_sound.mk_wav(self._freq, self._vol, self._time,
                                         self._rate)
        wav_wave2 = self._mk_sound.mk_wav(self._freq+10, self._vol, self._time,
                                         self._rate)
        self._mk_sound.play_wav(wav_wave1, blocking=False)
        time.sleep(0.5)
        self._mk_sound.play_wav(wav_wave2, blocking=False)
        time.sleep(3)

        self.__log.debug('done')

    def end(self):
        """end

        Call at the end of program.
        """
        self.__log.debug('doing ..')
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Description
''')
@click.argument('freq', type=float)
@click.option('--vol', '-v', 'vol', type=int, default=10000,
              help='volume < %s, default=%s' % (
                  MakeSound.VOL_MAX, MakeSound.DEF_VOL))
@click.option('--time', '-t', 'time', type=float, default=MakeSound.DEF_TIME,
              help='time [sec], default=%s' % MakeSound.DEF_TIME)
@click.option('--rate', '-r', 'rate', type=str, default=MakeSound.DEF_RATE,
              help='Sample reate default=%s' % MakeSound.DEF_RATE)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(freq, vol, time, rate, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('freq,vol,time,rate=%s', (freq, vol, time, rate))

    app = SampleApp(freq, vol, time, rate, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
