#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Make sound
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from my_logger import get_logger


# --- 以下、サンプル ---


import time
import pygame
from midi_tools import *
import CuiUtil


class SampleApp:
    """Sample application class
    """
    VOLUME_MAX = 1.0
    VOLUME_MIN = 0.05

    DEF_VOLUME = 0.2

    NOTE_BASE_MIN = 0
    NOTE_BASE_MAX = 117

    DEF_NOTE_BASE = 69  # C

    DEF_SEC = 0.15  # sec

    DEF_RATE = 44100  # Hz

    def __init__(self, midi_file, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)

        self._midi_file = midi_file

        self._note_base = self.DEF_NOTE_BASE
        self._vol = self.DEF_VOLUME
        self._sec = self.DEF_SEC
        self._rate = self.DEF_RATE

        self._active = False

        self._cui = CuiUtil.CuiKey([
            CuiUtil.CuiCmd('12345678', self.play),
            CuiUtil.CuiCmd(['KEY_UP', 'KEY_DOWN'], self.change_vol),
            CuiUtil.CuiCmd(['KEY_RIGHT', 'KEY_LEFT'], self.change_sec),
            CuiUtil.CuiCmd(['KEY_PGUP', 'KEY_PGDOWN'],
                           self.change_note_base),
            CuiUtil.CuiCmd(['q', 'KEY_ESCAPE'], self.quit)
        ], debug=self._dbg)

        pygame.mixer.init(channels=1)

    def change_sec(self, key_sym):
        """
        """
        self.__log.debug('key_sym=%a', key_sym)

        if key_sym == 'KEY_RIGHT':
            self._sec += 0.05

        if key_sym == 'KEY_LEFT':
            self._sec -= 0.05

            if self._sec <= 0:
                self._sec = 0.05
                self.__log.warning('fix: sec=%s', self._sec)

        print('sec=%.2f' % self._sec)

    def change_note_base(self, key_sym):
        """
        """
        self.__log.debug('key_sym=%a', key_sym)

        if key_sym == 'KEY_PGUP':
            self._note_base += 12

        if key_sym == 'KEY_PGDOWN':
            self._note_base -= 12

        if self._note_base < self.NOTE_BASE_MIN:
            self._note_base = self.NOTE_BASE_MIN
            self.__log.warning('fix: note_base=%s', self._note_base)

        if self._note_base > self.NOTE_BASE_MAX:
            self._note_base = self.NOTE_BASE_MAX
            self.__log.warning('fix: note_base=%s', self._note_base)

        print('note_base=%s' % self._note_base)

    def change_vol(self, sym):
        """
        """
        self.__log.debug('sym=%s', sym)

        if sym == 'KEY_UP':
            self._vol += 0.05

        if sym == 'KEY_DOWN':
            self._vol -= 0.05

        if self._vol < self.VOLUME_MIN:
            self._vol = self.VOLUME_MIN
            self.__log.warning('fix: vol=%s', self._vol)

        if self._vol > self.VOLUME_MAX:
            self._vol = self.VOLUME_MAX
            self.__log.warning('fix: vol=%s', self._vol)

        print('vol=%.2f' % self._vol)

    def play(self, key_sym):
        """
        """
        self.__log.debug('key_sym=%a', key_sym)

        offset_list = [0, 2, 4, 5, 7, 9, 11, 12]
        idx = '12345678'.index(key_sym)
        offset = offset_list[idx]

        note = self._note_base + offset
        self.__log.debug('note=%s', note)

        freq = note2freq(note)
        self.__log.debug('freq=%s', freq)

        wav = Wav(freq, self._sec, self._rate, debug=self._dbg)

        snd = pygame.sndarray.make_sound(wav.wav)
        snd.set_volume(self._vol)
        snd.play()

        print('note:%d, %.2fHz, %.2fsec, vol:%.2f, rate:%s' % (
            note, freq, self._sec, self._vol, self._rate))

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
