# MIDI-utils

MIDI tools: Parser, Player, etc.

MIDIライブラリ ``mido`` を使って、
より使いやすい形にパージングする。

簡単なプレーヤー、wav形式の音源ファイル作成ツール付き。

* 全トラックを合成
* channelを選択することが可能
* (イベント単位ではなく) note単位で解析
* note毎に、開始時刻と終了時刻を絶対時間(曲の開始からの秒数)で算出
* noteの情報(`NoteInfo`)は、
  `print()` や `str()` で簡単に内容を確認できる


## 1. TL;DR

Install
```bash
$ cd ~
$ python3 -m venv env1
$ cd env1
$ git clone https://github.com/ytani01/MIDI-utils.git
$ cd MIDI-utils
$ . ./bin/activate
(env1)$ pip install -U pip setuptools wheel
(env1)$ hash -r
(env1)$ pip install .
```

Execute parser
```bash
(env1)$ python -m miditools parse midi_file
```

Execute player
```bash
(env1)$ python -m miditools play midi_file
```

## 2. for detail

### 2.1 API

```bash
(env1)$ python3 -m pydoc miditools.Parser.parse
(env1)$ python3 -m pydoc miditools.Player.play
(env1)$ python3 -m pydoc miditools.Wav
```

### 2.2 parsed data

```bash
(env1)$ python3 -m pydoc miditools.NoteInfo
```

## 3. Sample program

sample_player.py
```python
#!/usr/bin/env python3

import sys
from miditools import *

pa = Parser()
pl = Player()

data = pa.parse(sys.argv[1])

pl.play(data)
```


## A. Reference

* [Mido - MIDI Objects for Python](https://mido.readthedocs.io/en/latest/)


## B. Misc

![](docs/mido_play.mp4)
