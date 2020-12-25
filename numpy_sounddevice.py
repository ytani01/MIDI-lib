#!/usr/bin/env python3
#
import numpy
import sounddevice

RATE = 44100  # sample rate

def mk_wav(freq, time, rate=RATE):
    samples = numpy.arange(rate * time) / rate
    wave = 10000 * numpy.sin(2 * numpy.pi * freq * samples)
    wav_wave = numpy.array(wave, dtype=numpy.int16)

    return wav_wave

def play(freq, time, rate=RATE):
    sounddevice.default.samplerate = rate
    sounddevice.play(mk_wav(freq, time, rate), blocking=True)
    
