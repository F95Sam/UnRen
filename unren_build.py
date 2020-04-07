#!/usr/bin/env python3

"""
This is a helper app for "UnRen" to collect, pack and embed needet tool-files
into the main script.

Requirements: py 3.6

The files get collected by a dir walker, filepath and data are stored as
k: v in a dict. The dict is then pickled (#1), base85 encoded (#2) and
as string embedded in a prepaired placeholder location in the main script.

#1 to get the bytestream the encoder func wants
#2 A compress. algor. like zip outputs a codestream which confuses python(breaks)
"""


# pylint: disable=c0103, c0301, w0511, w0611


__title__ = 'UnRen streambuilder'
__license__ = 'Apache-2'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.2.0-alpha'


import os
import sys
from pathlib import Path as pt
import pickle
import base64


def embed_stream(target_s, pack_stream):
    """Embed's the datastream in the unren script."""
    with pt(target_s).open('rb+') as ofi:
        data = ofi.read()
        ofi.seek(0)
        ofi.truncate()
        ofi.write(data.replace(b"_placeholder", pack_stream))


def tools_packer(tools_pth, pth_lst):
    """Packs the tools to a pickled and encoded stream."""
    store = {}
    for f_item in pth_lst:
        with pt(f_item).open('rb') as ofi:
            d_chunk = ofi.read()

        rel_fp = pt(f_item).relative_to(tools_pth)
        store[str(rel_fp)] = d_chunk

    # NOTE: To reduce size of output a compressor(zlib, lzma...) can be used in the middel of pickle and the encoder; Not at the end - isn't py code safe
    stream = base64.b85encode(pickle.dumps(store))
    return stream


def path_walker(tools_pth):
    """Walks the tools directory and collects a list of py files."""
    tool_lst = []
    for fpath, _subdirs, files in os.walk(tools_pth):
        for fln in files:
            if pt(fln).suffix in ['.py', '.pyc']:
                tool_lst.append(pt(fpath).joinpath(fln))
    return tool_lst


def ur_main():
    """This executes all program steps."""
    # QUESTION: I think paths could be fixed; eleminates cli parsing but rigide

    # hm... do we better use a absolute path
    # tools_pth = pt('/home/olli/Code/tst/ur_tools')
    # or relative in a fixed dir struct
    tools_pth = pt('ur_tools')
    if len(sys.argv) > 1:
        target_scr = sys.argv[1]
    else:
        target_scr = "ur_tester.py"
        # target_scr = "unren_py3.6.py"
        # print("Target path missing. \
        # Use: python3 unren_build.py '/path/to/target/script.py'")

    packlist = path_walker(tools_pth)
    stream = tools_packer(tools_pth, packlist)
    embed_stream(target_scr, stream)

    print("\nUnRen streambuilder:>> Task completed!\n")


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise f"Must be executed in Python 3.6 or later. You are running {sys.version}"
    ur_main()
