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


# pylint: disable=c0103, C0301, W0511, w0611, w0613


__title__ = 'UnRen builder'
__license__ = 'Apache-2'
__author__ = 'madeddy'
__status__ = 'Development'
__version__ = '0.11.1-alpha'


import os
import sys
import argparse
from pathlib import Path as pt
import pickle
import base64


class UrBuild:
    """
    Constructs from raw base files and different code parts the final
    executable scripts.
    (Class acts more as wrapper for easier var sharing without global.)
    """

    name = 'UnRen builder'
    # config  # hm...absolute or relative paths?
    tools_pth = pt('ur_tools').resolve(strict=True)
    snipped_pth = pt('ur_embed_rpy').resolve(strict=True)
    embed_lib = {b'console_placeholder': 'dev_con.rpy',
                 b'quick_placeholder': 'quick.rpy',
                 b'rollback_placeholder': 'rollback.rpy',
                 b'skip_placeholder': 'skip.rpy'}

    raw_py2 = 'ur_raw_27.py'
    raw_py3 = 'ur_raw_36.py'
    embed_py2 = 'ur_embed_27.py'
    embed_py3 = 'ur_embed_36.py'
    base_cmd = pt('ur_base.cmd').resolve(strict=True)

    dst_py2 = 'unren_py27.py'
    dst_py3 = 'unren_py36.py'
    dst_cmd2 = 'unren_27.cmd'
    dst_cmd3 = 'unren_36.cmd'

    def __init__(self):
        self.embed_dct = {}
        self.tool_lst = []
        self.toolstream = None
        self._tmp = None

    def read_filedata(self, src_file):
        """Opens a given file and returns the content as bytes type."""
        with src_file.open('rb') as ofi:
            self._tmp = ofi.read()
            return self._tmp  # needed for cmd_stream

    def embed_data(self, placeholder, embed_data):
        """Embed's the given data in target datastream."""
        self._tmp = self._tmp.replace(placeholder, embed_data)

    @staticmethod
    def write_filedata(dst_file, data):
        """Writes a new file with given content."""
        with dst_file.open('wb') as ofi:
            ofi.write(data)

    # Step 1a
    @staticmethod
    def read_rpy_cfg(src_rpy):
        """Reads the RenPy cfg data from a rpy file."""
        with pt(UrBuild.snipped_pth).joinpath(src_rpy).open('rb') as ofi:
            lines = ofi.readlines()
            cfg_txt = (8 * b' ').join(lines[4:]).rstrip()
        return cfg_txt

    def get_rpy_embeds(self):
        """Gets the cfg text from every listed file and embeds it in the target py."""
        for plh, src_rpy in UrBuild.embed_lib.items():
            self.embed_dct[plh] = self.read_rpy_cfg(src_rpy)

    # Step 1b; pack tools to py
    def tools_packer(self):
        """Packs the tools to a pickled and encoded stream."""
        plh = b"tool_placeholder"
        store = {}
        for f_item in self.tool_lst:
            with pt(f_item).open('rb') as ofi:
                d_chunk = ofi.read()

            rel_fp = pt(f_item).relative_to(UrBuild.tools_pth)
            store[str(rel_fp)] = d_chunk
        # NOTE: To reduce size of output a compressor(zlib, lzma...) can be used in
        # the middel of pickle and the encoder; Not at the end - isn't py code safe
        self.toolstream = base64.b85encode(pickle.dumps(store))
        self.embed_dct[plh] = self.toolstream

    def path_walker(self):
        """Walks the tools directory and collects a list of py files."""
        for fpath, _subdirs, files in os.walk(UrBuild.tools_pth):
            for fln in files:
                if pt(fln).suffix in ['.py', '.pyc']:
                    self.tool_lst.append(pt(fpath).joinpath(fln))

    def embed2py(self):
        """Embeds the rpy cfg snippeds in the py files.
        Constructs the tools stream and embeds it in the py file."""
        self.get_rpy_embeds()  # must be before `tools_packer`
        self.path_walker()
        self.tools_packer()

        for _key, _val in dict({UrBuild.raw_py2: UrBuild.dst_py2,
                                UrBuild.raw_py3: UrBuild.dst_py3}).items():
            raw_py, dst_py = pt(_key), pt(_val)
            self.read_filedata(raw_py)

            for plh, emb in self.embed_dct.items():
                self.embed_data(plh, emb)
            self.write_filedata(dst_py, self._tmp)

    # Step 2: Optional (just for the win cmd)
    def py2cmd(self):
        """Constructs the py stream and embeds it in the cmd file."""
        batch_plh = "batch_placeholder"
        for _key, _val in dict({UrBuild.embed_py2: UrBuild.dst_cmd2,
                                UrBuild.embed_py3: UrBuild.dst_cmd3}).items():
            embed_py, dst_cmd = pt(_key), pt(_val)
            embed_py_stream = self.read_filedata(embed_py)
            self.read_filedata(UrBuild.base_cmd)
            self.embed_data(batch_plh, embed_py_stream)
            self.write_filedata(dst_cmd, self._tmp)


def parse_args():
    """Provides argument parsing functionality on CLI. Obviously."""
    def valid_switch():
        """Helper function to determine if a task is choosen."""
        if not args.task:
            aps.print_help()
            raise argparse.ArgumentError(args.task, "\nNo task requested; "
                                         "either -1, -2 or -3 is required.")
    aps = argparse.ArgumentParser(
        description="Helper app to build the release versions of UnRen.",
        epilog="")
    switch = aps.add_mutually_exclusive_group()
    switch.add_argument('-makepy',
                        dest='task',
                        action='store_const',
                        const='part_1',
                        help="Executes step 1(a&b): embeds the RenPy config snippeds \
                        and tools into the raw Python scripts.")
    switch.add_argument('-makecmd',
                        dest='task',
                        action='store_const',
                        const='part_2',
                        help="Execute step 2: embeds the Python script into the cmd.")
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

    urb = UrBuild()
    # Step 1a & 1b  embed rpy cfg & tools in the raw py files
    if cfg.task == 'part_1':
        urb.embed2py()
    # Step 2 - embed py files in the cmd file
    elif cfg.task == 'part_2':
        urb.py2cmd()

    print("\nUnRen builder:>> Task completed!\n")


if __name__ == '__main__':
    build_main(parse_args())
