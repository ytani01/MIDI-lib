# midi-utils

MIDI utilities and test programs

## ToDo

### マルチトラックへの対応

* `note_on` .. `note_on` .. `note_off` .. `note_off` というパターンに対応
* mido.merge_tracks()を使わない
* トラックを選択可能にする

## TL;DR

Install
```bash
$ cd ~
$ python3 -m venv env1
$ cd env1
$ git clone https://github.com/ytani01/midi-utils.git
$ cd midi-utils
$ . ./bin/activate
(env1)$ pip install -r requirements.txt
```

Execute
```bash
$ ./MidiParser.py midi_file

$ ./MidiPaperTape.py midi_file
```


## A. Reference

* [Mido - MIDI Objects for Python](https://mido.readthedocs.io/en/latest/)

## B. Misc

![](docs/mido_play.mp4)
