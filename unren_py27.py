#!/usr/bin/env python2

"""
This is a wrapper app around tools for the works with RenPy files. It provides multiple
functionality through a simple text menu.
Abbilitys are unpacking RPA, decompiling rpyc and enabling respectively reactivating
diverse RenPy functions through script commands.
"""

# pylint: disable=c0301, w0511, w0603


import os
import sys
import argparse
import tempfile
import pickle
import base64
import textwrap

# NOTE: Needs the backported package pathlib2 installed
# win: python -m pip install pathlib2
# unix: python pip install pathlib2
# mac: sudo easy_install pip pip install pathlib2 (?)
from pathlib2 import Path as pt


# NOTE: py3.6 f-strings are not available in py2
# code from py3 script will need rework with the old % and .format styles


 # Subject to change; thats experimental
with open("version.txt", 'r') as ofi:
    VER_TXT = ofi.readline().strip()

__title__ = 'UnRen'
__license__ = 'Apache-2'
__author__ = 'F95sam, madeddy'
__status__ = 'Development'
__version__ = VER_TXT


# TODO: Placeholder: On completition of the python 3 version the code needs to be
# copied over and adjusted for python 2.7


if __name__ == '__main__':
    if not sys.version_info >= (2, 7):
        raise f"Must be executed in Python 2.7.x but not 3.x or later. You are running {sys.version}"
