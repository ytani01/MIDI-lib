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

from MyLogger import get_logger


# --- 以下、サンプル ---


import time
import MidiUtil
import WavUtil
import CuiUtil


class SampleApp:
    """Sample application class
    """
    VOLUME_MAX = 1.0
    VOLUME_MIN = 0.0

    DEF_VOLUME = 0.5

    DEF_NOTE_BASE = 69  # C

    DEF_SEC = 0.5  # sec

    DEF_RATE = 44100  # Hz

    __log = get_logger(__name__, False)

    def __init__(self, midi_file, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)

        self._midi_file = midi_file

        self._note_base = self.DEF_NOTE_BASE
        self._vol = self.DEF_VOLUME
        self._sec = self.DEF_SEC
        self._rate = self.DEF_RATE

        self._active = False

        self._mu = MidiUtil.Util(debug=self._dbg)

        self._cui = CuiUtil.CuiKey([
            CuiUtil.CuiCmd('123456789', self.play),
            CuiUtil.CuiCmd(['q', 'KEY_ESCAPE'], self.quit)
        ], debug=self._dbg)

    def play(self, key_sym):
        """
        """
        self.__log.debug('key_sym=%a', key_sym)

        note = self._note_base + int(key_sym) - 1
        self.__log.debug('note=%s', note)

        freq = self._mu.note2freq(note)
        self.__log.debug('freq=%s', freq)

        wav = WavUtil.Wav(freq, self._sec, self._rate, debug=self._dbg)
        wav.play(self._vol, blocking=False)

    def quit(self, key_sym):
        """
        """
        self.__log.debug('key_sym=%a', key_sym)

        self._active = False

    def main(self):
        """main
        """
        self.__log.debug('')

        self._cui.start()

        self._active = True

        while self._active:
            time.sleep(1)

        self.__log.debug('done')

    def end(self):
        """
        Call at the end of program.
        """
        self.__log.debug('doing ..')
        self._cui.end()
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Description
''')
@click.argument('midi_file', type=click.Path(exists=True), nargs=-1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)

    app = SampleApp(midi_file, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
