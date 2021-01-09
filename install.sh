#!/bin/sh -e
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`
MYDIR=`dirname $0`
BINDIR="$HOME/bin"

PKG_NAME="midilib"
WRAPPER_SCRIPT="MidiLib"

PKGS_TXT="pkgs.txt"

ENV_FILE="$BINDIR/$PKG_NAME.env"

BIN_FILES="$WRAPPER_SCRIPT"

#
# fuctions
#
cd_echo() {
    cd $1
    echo "### [ `pwd` ]"
    echo
}

#
# main
#
cd_echo $MYDIR
MYDIR=`pwd`
echo "MYDIR=$MYDIR"
echo

#
# install Linux packages
#
echo "### install Linux packages"
echo
sudo apt install `cat $PKGS_TXT`
echo

#
# venv
#
if [ -z $VIRTUAL_ENV ]; then
    if [ ! -f ../bin/activate ]; then
        echo
        echo "ERROR: Please create and activate Python3 Virtualenv(venv) and run again"
        echo
        echo "\$ cd ~"
        echo "\$ python -m venv env1"
        echo "\$ . ~/env1/bin/activate"
        echo
        exit 1
    fi
    echo "### activate venv"
    . ../bin/activate
fi
cd_echo $VIRTUAL_ENV

echo "### create $BINDIR/$ENV_FILE"
echo "VENVDIR=$VIRTUAL_ENV" >> $ENV_FILE
echo
cat $ENV_FILE
echo

#
# update pip, setuptools, and wheel
#
echo "### insall/update pip etc. .."
echo
pip install -U pip setuptools wheel
hash -r
echo
pip -V
echo

#
# install main package
#
cd_echo $MYDIR
echo "### install main python package"
echo
pip install .
echo

#
# install scripts
#
echo "### install scripts"
echo
if [ ! -d $BINDIR ]; then
    mkdir -pv $BINDIR
fi
cp -fv $BIN_FILES $BINDIR
echo

echo "### usage"
echo
$WRAPPER_SCRIPT
echo
