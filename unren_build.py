#!/usr/bin/env python3

"""
This is a helper app for "UnRen" to collect, pack and embed diff. module files
into the main script.

Requirements: py 3.6

The files get collected by a dir walker, filepath and data are stored as
k: v in a dict. The dict is then pickled (#1), base85 encoded (#2) and
as string embedded in a prepaired placeholder location in the main script.

#1 to get the bytestream the encoder func wants
#2 A compress. algor. like zip outputs a codestream which confuses python(breaks)
"""


# pylint: disable=c0103, c0301, w0511, w0611


__title__ = 'UnRen builder'
__license__ = 'Apache-2'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.7.0-alpha'


import os
import sys
import argparse
from pathlib import Path as pt
import pickle
import base64


# Support func; used by multiple parts
def embed_data(dst_file, data, placeholder):
    """Embed's the given data in a target script."""
    # FIXME: Placeholder must be flexible if this func is used by multiple tasks
    # use a variable instead...
    with pt(dst_file).open('rb+') as ofi:
        file_data = ofi.read()
        ofi.seek(0)
        ofi.truncate()
        ofi.write(file_data.replace(b"_placeholder", data))


# Part 3: Optional (just for the win cmd)
def duplicate_file(dst_file, data):
    """Writes a new file with given content."""
    with pt(dst_file).open('wb') as ofi:
        ofi.write(data)


def get_filedata(src_file):
    """Opens a given file and returns the content as bytes type."""
    with pt(src_file).open('rb') as ofi:
        file_data = ofi.read()
    return file_data


def py2cmd(embed_py2, embed_py3, base_cmd, dst_cmd2, dst_cmd3):
    """Constructs the py stream and embeds it in the cmd file."""
    placeholder = "batch_placeholder"
    cmd_stream = get_filedata(base_cmd)

    duplicate_file(dst_cmd2, cmd_stream)
    py_stream = get_filedata(embed_py2)
    embed_data(cmd_stream, py_stream, placeholder)

    duplicate_file(dst_cmd3, cmd_stream)
    py_stream = get_filedata(embed_py3)
    embed_data(cmd_stream, py_stream, placeholder)


# Part 2; pack tools to py
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


def tool2py(tools_pth, dst_py2, dst_py3):
    """Constructs the tools stream and embeds it in the py file."""
    placeholder = "tool_placeholder"
    packlist = path_walker(tools_pth)
    toolstream = tools_packer(tools_pth, packlist)
    # embed_data(dst_py2, toolstream, placeholder)
    embed_data(dst_py3, toolstream, placeholder)


# Part 1
def get_rpy_cfg(src_rpy):
    """Reads the RenPy cfg data from a rpy file."""
    with pt(src_rpy).open('rb') as ofi:
        lines = ofi.readlines()
        cfg_txt = lines[4:]
    return cfg_txt


def embed_rpycfg(dst_py):
    """Gets the cfg text from every listed file and embeds it in the target py."""
    # console_placeholder = "console_placeholder"
    # quick_placeholder = "quick_placeholder"
    # rollback_placeholder = "rollback_placeholder"
    # skip_placeholder = "skip_placeholder"

    rpy_lib = {"dev_con.rpy": "console_placeholder",
               "quick.rpy": "quick_placeholder",
               "rollback.rpy": "rollback_placeholder",
               "skip.rpy": "skip_placeholder"}
    for rpy_file, placeholder in rpy_lib.items():
        rpycfg_txt = get_rpy_cfg(rpy_file)
        embed_data(dst_py, rpycfg_txt, placeholder)


def rpycfg2py(src_py2, src_py3, embed_py2, embed_py3):
    """Embeds the rpy cfg snippeds in the py files."""
    embed_rpycfg(src_py2)
    embed_rpycfg(src_py3)
    embed_rpycfg(embed_py2)
    embed_rpycfg(embed_py3)


def parse_args():
    """Provides argument parsing functionality on CLI. Obviously."""
    aps = argparse.ArgumentParser(description="Helper app to build the release versions of UnRen.", epilog="")
    aps.add_argument('-1',
                     dest='task',
                     action='store_const',
                     const='part_1',
                     help="Execute step 1 - embeds the RenPy config snippeds.")
    aps.add_argument('-2',
                     dest='task',
                     action='store_const',
                     const='part_2',
                     help="Execute step 2 - embeds the tools into the Python scripts.")
    aps.add_argument('-3',
                     dest='task',
                     action='store_const',
                     const='part_3',
                     help="Execute step 3 - embeds the Python script into the cmd.")
    aps.add_argument('--version',
                     action='version',
                     version=f'%(prog)s : { __title__} {__version__}')
    return aps.parse_args()


def build_main(cfg):
    """This executes all program steps."""
    dst_py2 = "unren_py27.py"
    dst_py3 = "unren_py36.py"
    embed_py2 = "unren_py27_embed.py"
    embed_py3 = "unren_py36_embed.py"

    # Part 1
    if not sys.version_info[:2] >= (3, 6):
        raise Exception("Must be executed in Python 3.6 or later.\n"
                        f"You are running {sys.version}")
    if cfg.task == 'part_1':
        rpycfg2py(dst_py2, dst_py3, embed_py2, embed_py3)

    # Part 2 - embed tools in the py files  # hm...do we use a absolute path:
    # tools_pth = pt('/home/olli/Code/tst/ur_tools')
    # or relative path in a fixed dir struct:
    elif cfg.task == 'part_2':
        tools_pth = pt('ur_tools')
        tool2py(tools_pth, dst_py2, dst_py3)

    # part3 - embed py files in the cmd file
    elif cfg.task == 'part_3':
        base_cmd = "unren_base.cmd"
        dst_cmd2 = "unren_27.cmd"
        dst_cmd3 = "unren_36.cmd"
        py2cmd(embed_py2, embed_py3, base_cmd, dst_cmd2, dst_cmd3)

    print("\nUnRen builder:>> Task completed!\n")


if __name__ == '__main__':
    build_main(parse_args())
