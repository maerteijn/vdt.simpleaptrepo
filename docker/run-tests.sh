#!/bin/bash
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# runs the unittests
python3 -m pip install pip --upgrade
pip3 install -e .[dev]
make nosetest
