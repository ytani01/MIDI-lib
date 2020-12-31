# midi-utils

MIDI utilities and test programs

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

## 高速化の工夫

まじめに全てのnoteに対して音を生成すると時間がかかるので、
以下のような工夫をしている。

* 全ノートに対してでは無く、
  `(note_num, length)` をキーとしたパターンで作成
* `max_length` と `mini_length` を決め、範囲を限定
* `length` を 0.1 sec 単位に丸めて、パターンを減少

## A. Reference

* [Mido - MIDI Objects for Python](https://mido.readthedocs.io/en/latest/)

## B. Misc

![](docs/mido_play.mp4)
