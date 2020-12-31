#
# (c) 2020 Yoichi Tanibayashi
#
from . import Parser, Player, Wav
from .MyLogger import get_logger
import pygame
import click


class MidiApp:
    """
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, channel, parse_only=False,
                 rate=Player.DEF_RATE,
                 debug=False) -> None:
        """
        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s, channel=%s, parse_only=%s',
                         midi_file, channel, parse_only)
        self.__log.debug('rate=%s', rate)

        self._midi_file = midi_file
        self._channel = channel
        self._parse_only = parse_only
        self._rate = rate

        self._parser = Parser(debug=self._dbg)
        self._player = Player(rate=self._rate, debug=self._dbg)

    def main(self) -> None:
        """
        """
        self.__log.debug('')

        parsed_data = self._parser.parse(self._midi_file, self._channel)

        if self._dbg or self._parse_only:
            for d in parsed_data['data']:
                print(d)

            print('channel_set=', parsed_data['channel_set'])

        if self._parse_only:
            return

        self._player.play(parsed_data)

    def end(self) -> None:
        """
        """
        pass


class WavApp:
    """
    """

    __log = get_logger(__name__, False)

    def __init__(self, freq, outfile, vol, sec, rate=Wav.DEF_RATE,
                 debug=False) -> None:
        """constructor

        Parameters
        ----------
        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('freq,vol,sec,rate=%s', (freq, vol, sec, rate))
        self.__log.debug('outfile=%s', outfile)

        self._freq = freq
        self._outfile = outfile
        self._vol = vol
        self._sec = sec
        self._rate = rate

        pygame.mixer.init(frequency=self._rate, channels=1)

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


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS, help='''
python3 -m midi_tools COMMAND [OPTIONS] [ARGS] ...
''')
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print()
        print('Please specify subcommand')
        print()
        print(ctx.get_help())
    else:
        print()
        print('midi_tools command=%s\n' % ctx.invoked_subcommand)


@cli.command(context_settings=CONTEXT_SETTINGS, help='''
MIDI parser
''')
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--debug', '-d', 'dbg', is_flag=True, default=False,
              help='debug flag')
def parse(midi_file, channel, dbg) -> None:
    """
    parser main
    """
    log = get_logger(__name__, dbg)

    app = MidiApp(midi_file, channel, parse_only=True,
                  debug=dbg)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()


@cli.command(context_settings=CONTEXT_SETTINGS, help='''
MIDI player
''')
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--rate', '-r', 'rate', type=int,
              default=Player.DEF_RATE,
              help='sampling rate, default=%s Hz' % Player.DEF_RATE)
@click.option('--debug', '-d', 'dbg', is_flag=True, default=False,
              help='debug flag')
def play(midi_file, channel, rate, dbg) -> None:
    """
    player main
    """
    log = get_logger(__name__, dbg)

    app = MidiApp(midi_file, channel, parse_only=False, rate=rate,
                  debug=dbg)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()


@cli.command(context_settings=CONTEXT_SETTINGS, help='''
Wav format sound tool
''')
@click.argument('freq', type=float)
@click.argument('outfile', type=click.Path(), nargs=-1)
@click.option('--vol', '-v', 'vol', type=float, default=Wav.DEF_VOL,
              help='volume <= %s, default=%s' % (
                  Wav.VOL_MAX, Wav.DEF_VOL))
@click.option('--sec', '-t', '-s', 'sec', type=float, default=Wav.DEF_SEC,
              help='sec [sec], default=%s sec' % Wav.DEF_SEC)
@click.option('--rate', '-r', 'rate', type=int, default=Wav.DEF_RATE,
              help='Sampling reate, default=%s Hz' % Wav.DEF_RATE)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def wav(freq, outfile, vol, sec, rate, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('freq,vol,sec,rate=%s', (freq, vol, sec, rate))
    __log.debug('outfile=%s', outfile)

    app = WavApp(freq, outfile, vol, sec, rate, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    cli()
