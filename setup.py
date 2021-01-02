import os
import sys
from setuptools import setup, find_packages

def read_requirements():
    """Parse requirements from requirements.txt."""
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements

setup(
    name='miditools',
    version='0.0.2',
    description='MIDI tools',
    long_description='MIDI Parser, Player, Wav tools',
    author='Yoichi Tanibayashi',
    author_email='yoichi@tanibayashi.jp',
    url='https://github.com/ytani01/MIDI-utils/',
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Natural Language :: Japanese"
    ],
    install_requires=read_requirements(),
    packages=['miditools']
)
