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

import WavUtil
import MidiUtil
from MyLogger import get_logger


class SampleApp:
    """Sample application class
    """
    __log = get_logger(__name__, False)

    def __init__(self, sec, rate, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('sec,rate=%s', (sec, rate))

        self._sec = sec
        self._rate = rate

        self._mu = MidiUtil.Util()

    def main(self):
        """main
        """
        self.__log.debug('')

        for note in range(0, 128):
            fname = 'note_wav/note%03d.wav' % note
            self.__log.info('fname=%s', fname)
            freq = self._mu.note2freq(note)
            wav = WavUtil.Wav(freq, sec=self._sec, rate=self._rate)
            wav.save(fname)

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
@click.option('--sec', '-t', '-s', 'sec', type=float,
              default=WavUtil.Wav.DEF_SEC,
              help='sec [sec], default=%s' % WavUtil.Wav.DEF_SEC)
@click.option('--rate', '-r', 'rate', type=int,
              default=WavUtil.Wav.DEF_RATE,
              help='Sample reate default=%s' % WavUtil.Wav.DEF_RATE)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(sec, rate, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('sec,rate=%s', (sec, rate))

    app = SampleApp(sec, rate, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
