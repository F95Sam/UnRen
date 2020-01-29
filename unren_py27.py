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
from pathlib import Path as pt
import textwrap
import argparse


 # Subject to change
__title__ = 'UnRen'
__license__ = 'Apache-2'
__author__ = 'F95sam, madeddy'
__status__ = 'Development'
__version__ = '0.1.0-alpha'


# TODO: Placeholder: On completition of the python 3 version the code needs to be
# copied over and adjusted for python 2.7


if __name__ == '__main__':
    if not sys.version_info >= (2, 7):
        raise f"Must be executed in Python 3.6 or later. You are running {sys.version}"
