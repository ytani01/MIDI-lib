# MIDI-utils

MIDI utilities and test programs

midoを使って、より使いやすい形にパージングする。

* 全トラックを合成
* channelを選択することが可能
* イベント単位では無く、note単位で解析
* note毎に、開始時刻と終了時刻を絶対時間(曲の開始からの秒数)で算出
* noteの情報(`NoteInfo`)は、
  `print()` や `str()` で簡単に内容を確認できる


## ToDo

* Player.play()で、
  時間を監視して、ズレをより少なくする。


## 1. TL;DR

Install
```bash
$ cd ~
$ python3 -m venv env1
$ cd env1
$ git clone https://github.com/ytani01/MIDI-utils.git
$ cd MIDI-utils
$ . ./bin/activate
(env1)$ pip install -r requirements.txt
```

Execute parser
```bash
$ python -m midi_tools parse midi_file
```

Execute player
```bash
$ python -m midi_tools play midi_file
```

## 2. for detail

### 2.1 API

```bash
python3 -m pydoc midi_tools.Parser.parse
python3 -m pydoc midi_tools.Player.play
```

### 2.2 parsed data

```bash
python3 -m pydoc midi_tools.NoteInfo
```

## 3. Sample program

sample_player.py
```python
#!/usr/bin/env python3

import sys
from midi_tools import *

pa = Parser()
pl = Player()

data = pa.parse(sys.argv[1])
pl.play(data)
```


## A. Reference

* [Mido - MIDI Objects for Python](https://mido.readthedocs.io/en/latest/)


## B. Misc

![](docs/mido_play.mp4)
