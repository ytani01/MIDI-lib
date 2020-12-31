#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
SimpleMidiPlayer.py
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from MyLogger import get_logger


# --- 以下、サンプル ---


import pygame
import mido
import glob


class SampleApp:
    """Sample application class
    """
    VOLUME_MAX = 1.0
    VOLUME_MIN = 0.0

    DEF_VOLUME = 0.18

    __log = get_logger(__name__, False)

    def __init__(self, midi_file, vol, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s, vol=%s', midi_file, vol)

        self._midi_file = midi_file

        if vol > self.VOLUME_MAX:
            vol = self.VOLUME_MAX
            self.__log.debug('fix: vol=%s', vol)

        if vol < self.VOLUME_MIN:
            vol = self.VOLUME_MIN
            self.__log.debug('fix: vol=%s', vol)

        self._vol = vol

        pygame.mixer.init()

        self._midi = mido.MidiFile(self._midi_file)

        self._snd = self.load_wav()

    def load_wav(self):
        glob_pattern = "note_wav/note*.wav"
        wav_files = sorted(glob.glob(glob_pattern))

        snd_list = []
        for f in wav_files:
            snd = pygame.mixer.Sound(f)
            snd.set_volume(self._vol)
            snd_list.append(snd)

        self.__log.debug('done')

        return snd_list

    def main(self):
        """main
        """
        self.__log.debug('')

        msg = self._midi.play()
        self.__log.debug('play(): done')

        for m in msg:
            if m.type != 'note_on':
                continue

            if m.velocity == 0:
                continue

            self._snd[m.note].play(fade_ms=10, maxtime=900)
            print('channel:%s note:%s, velocity:%s' % (
                m.channel, m.note, m.velocity))

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
Simple MIDI player
''')
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--vol', '-v', 'vol', type=float,
              default=SampleApp.DEF_VOLUME,
              help='volume: 0 .. 1.0, default=%s' % SampleApp.DEF_VOLUME)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, vol, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)

    app = SampleApp(midi_file, vol, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
