#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser for

### for detail and simple usage

$ python3 -m pydoc mu


### API

see comment of ``mu`` class


### sample program

$ ./mu.py file.mid

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import time
import pygame
from WavUtil import Wav
from midi_utils import note2freq
import midi_parser
from MyLogger import log, get_logger, set_debug


class Player:
    """
    MIDI parser for Music Box

    * チャンネルを選択することができる。


    Simple Usage
    ------------
    ============================================================
    import mu

    parser = mu.Parser(midi_file)

    midi_data = parser.parse()
    ============================================================

    """
    SND_RATE = 11025
    SND_LEN_MAX = 1.2
    SND_LEN_MIN = 0.1

    SND_PLAY_FACTOR = 0.95

    __log = get_logger(__name__, False)

    def __init__(self, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('')

        pygame.mixer.init(frequency=self.SND_RATE, channels=1)

        self._snd = {}

    def snd_key(self, note_data):
        """
        """
        sec = note_data.length()

        if sec > self.SND_LEN_MAX:
            sec = self.SND_LEN_MAX

        if sec < self.SND_LEN_MIN:
            sec = self.SND_LEN_MIN

        key_sec = '%.1f' % sec
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

            if sec > self.SND_LEN_MAX:
                sec = self.SND_LEN_MAX

            if sec < self.SND_LEN_MIN:
                sec = self.SND_LEN_MIN

            self.__log.info('%s', key)

            wav = Wav(freq, sec, self.SND_RATE, debug=self._dbg).wav

            self._snd[key] = pygame.sndarray.make_sound(wav)

        return

    def play_sound(self, note_data):
        """
        """
        key = self.snd_key(note_data)

        snd = self._snd[key]
        vol = note_data.velocity / 128 / 8
        maxtime=int(self.SND_LEN_MAX * self.SND_PLAY_FACTOR * 1000)

        snd.set_volume(vol)
        snd.play(fade_ms=5, maxtime=maxtime)

    def play(self, parsed_midi):
        """
        """
        channel_set = parsed_midi['channel_set']
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

            if d.channel not in channel_set:
                continue

            if d.velocity == 0:
                continue

            self.__log.info('(%4d) %s', i, d)
            self.play_sound(d)
#            threading.Thread(target=self.play_sound, args=(d,),
#                             daemon=True).start()


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, channel=[], debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        channel: list of int
            MIDI channel

        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('channel=%s', channel)

        self._midi_file = midi_file
        self._channel = channel

        self._parser = midi_parser.Parser(debug=self._dbg)
        self._player = Player(debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        parsed_data = self._parser.parse(self._midi_file, self._channel)

        interval = []

        print('parsed data ..')
        for i, d in enumerate(parsed_data['data']):

            if d.length() > 0:
                interval.append(round(d.length(), 3))

            if d.velocity == 0:
                continue

            print('(%4d) %s' % (i, d))

        print('channel_set=%s' % (parsed_data['channel_set']))
        interval = sorted(list(set(interval)))

        self._player.play(parsed_data)

        self.__log.debug('done')

    def end(self):
        """ Call at the end of program.
        """
        self.__log.debug('doing ..')
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
MidiUtil sample program
''')
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--debug', '-d', 'dbg', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, channel, dbg):
    """サンプル起動用メイン関数
    """
    set_debug(dbg)
    log.debug('midi_file=%s', midi_file)
    log.debug('channel=%s', channel)

    app = SampleApp(midi_file, channel, debug=dbg)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
