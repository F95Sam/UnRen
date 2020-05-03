#!/usr/bin/env python3

"""
This is a helper app for "UnRen" to collect, pack and embed diff. module files
into the main script.

Requirements: py 3.6
Step 1:
Reads the content of few RenPy script files and embeds it into the py files.

Step 2:
The files get collected by a dir walker, filepath and data are stored as
k: v in a dict. The dict is then pickled (#1), base85 encoded (#2) and
embedded in a prepaired placeholder location in the main script.

#1 to get the bytestream the encoder func wants
#2 A compress. algorythm like zip outputs a codestream which confuses python(breaks)

Step 3:
Embeds the previously prepaired python script into a Win command file.
"""


# pylint: disable=c0103, c0301, w0511, w0611, w0613


__title__ = 'UnRen builder'
__license__ = 'Apache-2'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.10.0-alpha'


import os
import sys
import argparse
from pathlib import Path as pt
import pickle
import base64


# Support func; used by multiple steps
def embed_data(dst_file, data, placeholder):
    """Embed's the given data in a target script."""
    with dst_file.open('rb+') as ofi:
        file_data = ofi.read()
        ofi.seek(0)
        ofi.truncate()
        ofi.write(file_data.replace(placeholder, data))


# Step 1
def get_rpy_cfg(src_rpy):
    """Reads the RenPy cfg data from a rpy file."""
    with pt('rpy_embeds').joinpath(src_rpy).open('rb') as ofi:
        lines = ofi.readlines()
        cfg_txt = (8 * b' ').join(lines[4:]).rstrip()
    return cfg_txt


def embed_rpycfg(dst_py):
    """Gets the cfg text from every listed file and embeds it in the target py."""
    # TODO: placeholders in main py script
    rpy_lib = {"dev_con.rpy": b"console_placeholder",
               "quick.rpy": b"quick_placeholder",
               "rollback.rpy": b"rollback_placeholder",
               "skip.rpy": b"skip_placeholder"}
    for rpy_cfg, placeholder in rpy_lib.items():
        rpycfg_txt = get_rpy_cfg(rpy_cfg)
        embed_data(dst_py, rpycfg_txt, placeholder)


def rpycfg2py(src_py2, src_py3):
    """Embeds the rpy cfg snippeds in the py files."""
    # embed_rpycfg(src_py2)
    embed_rpycfg(src_py3)


# Step 2; pack tools to py
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
    placeholder = b"tool_placeholder"
    packlist = path_walker(tools_pth)
    toolstream = tools_packer(tools_pth, packlist)
    # embed_data(dst_py2, toolstream, placeholder)
    embed_data(dst_py3, toolstream, placeholder)


# Step 3: Optional (just for the win cmd)
def duplicate_file(dst_file, data):
    """Writes a new file with given content."""
    with dst_file.open('wb') as ofi:
        ofi.write(data)


def get_filedata(src_file):
    """Opens a given file and returns the content as bytes type."""
    with src_file.open('rb') as ofi:
        file_data = ofi.read()
    return file_data


def py2cmd(embed_py2, embed_py3, base_cmd, dst_cmd2, dst_cmd3):
    """Constructs the py stream and embeds it in the cmd file."""
    placeholder = "batch_placeholder"
    cmd_stream = get_filedata(base_cmd)

    # duplicate_file(dst_cmd2, cmd_stream)
    # py_stream = get_filedata(embed_py2)
    # embed_data(cmd_stream, py_stream, placeholder)

    duplicate_file(dst_cmd3, cmd_stream)
    py_stream = get_filedata(embed_py3)
    embed_data(cmd_stream, py_stream, placeholder)


def parse_args():
    """Provides argument parsing functionality on CLI. Obviously."""
    def valid_switch():
        """Helper function to determine if a task is choosen."""
        if not args.task:
            aps.print_help()
            raise argparse.ArgumentError(args.task, f"\nNo task requested; " \
                                         "either -1, -2 or -3 is required.")
    aps = argparse.ArgumentParser(
        description="Helper app to build the release versions of UnRen.",
        epilog="")
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
    args = aps.parse_args()
    valid_switch()
    return args


def build_main(cfg):
    """This executes all program steps."""
    if not sys.version_info[:2] >= (3, 6):
        raise Exception("Must be executed in Python 3.6 or later.\n"
                        f"You are running {sys.version}")
    # config  # hm...absolute or relative paths?
    tools_pth = pt('ur_tools').resolve(strict=True)
    dst_py2 = pt('unren_py27.py').resolve(strict=True)
    dst_py3 = pt('unren_py36.py').resolve(strict=True)
    embed_py2 = pt('unren_py27_embed.py').resolve(strict=True)
    embed_py3 = pt('unren_py36_embed.py').resolve(strict=True)
    base_cmd = pt('unren_base.cmd').resolve(strict=True)
    dst_cmd2 = pt('unren_27.cmd')
    dst_cmd3 = pt('unren_36.cmd')

    # Step 1
    if cfg.task == 'part_1':
        rpycfg2py(dst_py2, dst_py3)
    # Step 2 - embed tools in the py files
    elif cfg.task == 'part_2':
        tool2py(tools_pth, dst_py2, dst_py3)
    # Step 3 - embed py files in the cmd file
    elif cfg.task == 'part_3':
        py2cmd(embed_py2, embed_py3, base_cmd, dst_cmd2, dst_cmd3)

    print("\nUnRen builder:>> Task completed!\n")


if __name__ == '__main__':
    build_main(parse_args())
