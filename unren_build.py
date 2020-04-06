#!/usr/bin/env python3

"""
This is a helper app for "UnRen" to collect, pack and embed needet tool-files
into the main script.

Requirements: py 3.6 and "in_place" package

The files get collected by a dir walker, filepath and data are stored as
k: v in a dict. The dict is then pickled (#1), base85 encoded (#2) and
as string embeded in a prepaired placeholder location in the main script.

#1 to get the bytestream the encoder wants
#2 A compress. algor. like zip outputs a codestream which confuses python(breaks)
"""


# pylint: disable=c0103, c0301, w0511, w0611


__title__ = 'UnRen streambuilder'
__license__ = 'Apache-2'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.1.0-alpha'


import os
import sys
from pathlib import Path as pt
import pickle
import base64
import in_place


def tools_packer(tools_p, target_sc, pth_lst):
    """Packs the tools in the unren script."""
    store = {}
    for f_item in pth_lst:
        with pt(f_item).open('rb') as ofi:
            d_chunk = ofi.read()

        rel_fp = pt(f_item).relative_to(tools_p)
        store[str(rel_fp)] = d_chunk

    # NOTE: To reduce size of output a compressor(zlib, lzma...) can be used in the middel of pickle and the encoder; Not at the end - isn't py code safe
    stream = base64.b85encode(pickle.dumps(store))
    with in_place.InPlace(target_sc, mode='b', backup_ext='.bup') as ofi:
        for line in ofi:
            ofi.write(line.replace(b"_placeholder", stream))


def path_walker(tools_p):
    """Walks the tools directory and collects a list of py files."""
    tool_lst = []
    for fpath, _subdirs, files in os.walk(tools_p):
        for fln in files:
            if pt(fln).suffix in ['.py', '.pyc']:
                tool_lst.append(pt(fpath).joinpath(fln))
    return tool_lst


def ur_main():
    """This executes all program steps."""
    # QUESTION: I think paths should be fixed in the end; no need for cli parsing

    # hm... better a absolute path
    # tools_p = pt('/home/olli/Code/tst/ur_tools')
    # or relative in a fixed dir struct
    tools_p = pt('ur_tools')
    # target script
    outp_s = 'ur_tester.py'

    packlist = path_walker(tools_p)
    tools_packer(tools_p, outp_s, packlist)

    print("\n>> Completed!\n")


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise f"Must be executed in Python 3.6 or later. You are running {sys.version}"
    ur_main()
