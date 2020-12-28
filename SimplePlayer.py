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
import threading
from MyLogger import get_logger


class Wav:
    """Wav

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
    """
    DEF_SEC = 0.5  # sec
    DEF_RATE = 44100  # Hz
    VOL_MAX = 60000
    DEF_VOL = 3000

    __log = get_logger(__name__, False)

    def __init__(self, freq, sec=DEF_SEC, rate=DEF_RATE, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('freq,sec,rate=%s', (freq, sec, rate))

        self._wav = self.mk_wav(freq, sec, rate)

    def mk_wav(self, freq, sec=DEF_SEC, rate=DEF_RATE):
        """method1

        Parameters
        ----------
        """
        self.__log.debug('freq,sec,rate=%s', (freq, sec, rate))

        samples = numpy.arange(0, rate * sec)
        sin_wave1 = numpy.sin(2 * numpy.pi * freq * samples / rate)
        # 16bit 符号付き整数に変換
        sin_wave2 = [int(x * 32767.0) for x in sin_wave1]

        return sin_wave2

    def save(self, outfile, rate=DEF_RATE):
        """
        outfile: str
        """
        self.__log.debug('outfile=%s, rate=%s', outfile, rate)

        w_write = wave.Wave_write(outfile)
        w_write.setparams((
            1, 2, rate, len(self._wav), 'NONE', 'not compressed'))
        w_write.writeframes(array.array('h', self._wav).tobytes())
        w_write.close()

    def play(self, vol=DEF_VOL, rate=DEF_RATE, blocking=True):
        """
        Parameters
        ----------
        rate: int
        blocking: bool
        """
        self.__log.debug('vol=%s, rate=%s, blocking=%s',
                         vol, rate, blocking)

        if vol > self.VOL_MAX:
            vol = self.VOL_MAX
            self.__log.warning('fix: vol=%s', vol)

        w_out = [int(x * vol) for x in self._wav]
        sounddevice.play(w_out, rate, blocking=blocking)


# --- 以下、サンプル ---


import pygame
import mido
import glob
import MidiUtil


class SampleApp:
    """Sample application class
    """

    __log = get_logger(__name__, False)

    def __init__(self, midi_file, vol, debug=False):
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)

        self._midi_file = midi_file
        self._vol = vol

        pygame.mixer.init()

        self._midi = mido.MidiFile(self._midi_file)
        self._mu = MidiUtil.Util()

        self._snd = self.load_wav()

    def load_wav(self):
        glob_pattern = "note_wav/*.wav"
#        glob_pattern = "../MusicBox/wav/3*.wav"
        wav_files = sorted(glob.glob(glob_pattern))
        print(len(wav_files))

        snd_list = []
        for f in wav_files:
            snd = pygame.mixer.Sound(f)
            snd.set_volume(self._vol)
            snd_list.append(snd)
            
        return snd_list

    def main(self):
        """main
        """
        self.__log.debug('')

        msg = self._midi.play()

        for m in msg:
            if m.type != 'note_on':
                continue

            if m.velocity == 0:
                continue

            print('channel:%s note:%s, velocity:%s' % (
                m.channel, m.note, m.velocity))
            # self._snd[m.note].play(fade_ms=100)
            threading.Thread(target=self._snd[m.note].play).start()

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
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--vol', '-v', 'vol', type=float, default=0.25,
              help='volume')
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
