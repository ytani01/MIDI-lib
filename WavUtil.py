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
import wave
import array
from MyLogger import get_logger


class Wav:
    """Wav

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
    """
    DEF_SEC = 0.5  # sec
    DEF_RATE = 12800  # Hz
    VOL_MAX = 1.0
    VOL_MIN = 0.0
    DEF_VOL = 0.5

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

    def play(self, vol=DEF_VOL, blocking=False):
        """
        Parameters
        ----------
        vol: float
        blocking: bool
        """
        self.__log.debug('vol=%s, blocking=%s', vol, blocking)

        if vol > self.VOL_MAX:
            vol = self.VOL_MAX
            self.__log.warning('fix: vol=%s', vol)

        if vol < self.VOL_MIN:
            vol = self.VOL_MIN
            self.__log.warning('fix: vol=%s', vol)

        w_list = [int(x * vol) for x in self.wav]
        w_out = numpy.array(w_list, dtype=numpy.int16)

        sounddevice.play(w_out, self._rate, blocking=blocking)


# --- 以下、サンプル ---


class SampleApp:
    """Sample application class
    """

    __log = get_logger(__name__, False)

    def __init__(self, freq, outfile, vol, sec, rate, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('freq,vol,sec,rate=%s', (freq, vol, sec, rate))
        self.__log.debug('outfile=%s', outfile)

        self._freq = freq
        self._outfile = outfile
        self._vol = vol
        self._sec = sec
        self._rate = rate

    def main(self):
        """main
        """
        self.__log.debug('')

        wav = Wav(self._freq, self._sec, self._rate,
                  debug=self._dbg)

        wav.play(self._vol)

        if len(self._outfile) > 0:
            wav.save(self._outfile[0])

        self.__log.debug('done')

    def end(self):
        """
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
@click.argument('outfile', type=click.Path(), nargs=-1)
@click.option('--vol', '-v', 'vol', type=float, default=Wav.DEF_VOL,
              help='volume <= %s, default=%s' % (
                  Wav.VOL_MAX, Wav.DEF_VOL))
@click.option('--sec', '-t', '-s', 'sec', type=float, default=Wav.DEF_SEC,
              help='sec [sec], default=%s' % Wav.DEF_SEC)
@click.option('--rate', '-r', 'rate', type=int, default=Wav.DEF_RATE,
              help='Sample reate default=%s' % Wav.DEF_RATE)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(freq, outfile, vol, sec, rate, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('freq,vol,sec,rate=%s', (freq, vol, sec, rate))
    __log.debug('outfile=%s', outfile)

    app = SampleApp(freq, outfile, vol, sec, rate, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
