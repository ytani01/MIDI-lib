# MIDI-lib

Simple MIDI library: Parser, Player, etc.

Python向け MIDIライブラリ ``Mido`` を使って、
より使いやすい形にパージングするライブラリです。

簡単なプレーヤー、wav形式の音源ファイル作成機能などもあります。

特徴
* 全トラックを合成
* channelを選択することが可能
* (イベント単位ではなく) note単位で解析
* note毎に、開始時刻と終了時刻を絶対時間(曲の開始からの秒数)で算出
* noteの情報(`NoteInfo`)は、
  `print()` や `str()` で簡単に内容を確認できる


## TL;DR

Sample program
```python
#!/usr/bin/env python3

import sys
from midilib import *

midi_file = sys.argv[1]
pa = Parser()
pl = Player()

parsed_data = pa.parse(midi_file)

pl.play(parsed_data)
```

## 1. Install

```bash
$ cd ~
$ python3 -m venv env1
$ cd env1
$ . ./bin/activate
(env1)$ git clone https://github.com/ytani01/MIDI-utils.git
(env1)$ cd MIDI-utils
(env1)$ pip install -U pip setuptools wheel
(env1)$ hash -r
(env1)$ pip install .
```

## 2. デモ実行

### 2.1 Execute parser
```bash
(env1)$ python -m midilib parse midi_file
```

### 2.2 Execute player
```bash
(env1)$ python -m midilib play midi_file
```


## 3. for detail

### 3.1 API

パージングする関数
```bash
(env1)$ python3 -m pydoc midilib.Parser.parse
```

パージング結果を受けて音楽を再生する関数
```bash
(env1)$ python3 -m pydoc midilib.Player.play
```

指定されてた周波数の音源データ(wav形式)を作成/再生/保存するクラス
```bash
(env1)$ python3 -m pydoc midilib.Wav
```

ノート番号を周波数に変換する関数
```bash
(env1)$ python3 -m pytoc midilib.note2freq
```

### 3.2 parsed data

```
parsed_data = {
  'channel_set': { 元ファイルに含まれている全チャンネル番号 },
  'note_info': [ ノート情報のリスト ]
}
```

パージング結果に含まれているノート情報
(parsed_data['note_info'])
```bash
(env1)$ python3 -m pydoc midilib.NoteInfo
```


## A. Reference

* [Mido - MIDI Objects for Python](https://mido.readthedocs.io/en/latest/)


## B. Misc

![](docs/mido_play.mp4)
