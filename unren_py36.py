#!/usr/bin/env python3

"""
This is a wrapper app around tools for the works with RenPy files. It provides multiple
functionality through a simple text menu.

Requirements: python 3.6+

Abbilitys are unpacking rpa files, decompiling rpyc(py2!) files and enabling respectively
reactivating diverse RenPy functions by script commands.
"""

# pylint: disable=c0103, c0301, c0415, w0511, w0603


import os
import sys
import argparse
from pathlib import Path as pt
import shutil
import tempfile
import textwrap
import pickle
import base64



__title__ = 'UnRen'
__license__ = 'Apache-2'
__author__ = 'F95sam, madeddy'
__status__ = 'Development'
__version__ = '0.5.0-alpha'


_TOOLSTREAM = r"_placeholder"


class UnRen:
    """
    UnRen class for all the wanted tasks. Args:
        Positional: {targetpath} takes a `pathlike` or string
        Keyword: {verbose=[0|1|2]} information output level; defaults to 1
    """

    name = "UnRen"
    verbosity = 1
    count = {'rpa_f_found': 0, 'rpyc_f_found': 0}

    menu_screen = fr"""
       __  __      ____
      / / / /___  / __ \___  ____
     / / / / __ \/ /_/ / _ \/ __ \
    / /_/ / / / / _, _/  __/ / / /
    \____/_/ /_/_/ |_|\___/_/ /_/  Version {__version__}

      Available Options:

      1) Extract all RPA packages
      2) Decompile rpyc files
      3) Enable Console and Developer Menu
      4) Enable Quick Save and Quick Load
      5) Force enable skipping of unseen content
      6) Force enable rollback (scroll wheel)
      0) All six options above

      x) Exit this application
    """
    menu_opts = {'1': 'extract',
                 '2': 'decompile',
                 '3': 'console',
                 '4': 'quick',
                 '5': 'skip',
                 '6': 'rollback',
                 '0': 'all_opts',
                 'x': '_exit'}


    def __init__(self, target='', verbose=None):
        if verbose is not None:
            UnRen.verbosity = verbose
        self.in_pth = pt(target)
        self.base_pth = None
        self.game_pth = None
        self.ur_tmp_dir = None
        self.rpakit = None
        # NOTE: Unneeded till supporting py3
        # self.unrpyc = None


    # FIXME: newline with textwrap... how?
    # test inf functionality some more
    @classmethod
    def inf(cls, inf_level, msg, m_sort=None):
        """Outputs by the current verboseness level allowed self.infos."""
        if cls.verbosity >= inf_level:  # self.tty ?
            ind1 = f"{cls.name}:\x1b[32m >> \x1b[0m"
            ind2 = " " * 10
            if m_sort == 'note':
                ind1 = f"{cls.name}:\x1b[93m NOTE \x1b[0m> "
                ind2 = " " * 13
            elif m_sort == 'warn':
                ind1 = f"{cls.name}:\x1b[31m WARNING \x1b[0m> "
                ind2 = " " * 17
            print(textwrap.fill(msg, width=90, initial_indent=ind1, subsequent_indent=ind2, replace_whitespace=False))

    def import_tools(self):
        """This runs a deferred import of the tools due to the tools just usable after our script runs already."""
        try:
            sys.path.append(self.ur_tmp_dir)
            self.rpakit = __import__('rpakit', globals(), locals())

            # WARNING: Do not try to import `unrpyc`. py2 only for now!
            # self.unrpyc = __import__('unrpyc', globals(), locals())
        except ImportError:
            raise ImportError("Unable to import the tools from temp directory.")

    @staticmethod
    def make_rpy_cfg(outfile):
        """Constructs the rpy config file and adds header code."""
        header_txt = """\
            # RenPy script file
            # Config changes; written by UnRen

            init 999 python:
        """
        with outfile.open('w') as ofi:
            print(textwrap.dedent(header_txt), file=ofi)

    # IDEA: Rework write config functionality to less complexity, methods ...
    def write_rpy_cfg(self, cfg_id, cfg_code, cfg_inf):
        """Writes given text to the file."""
        outfile = pt(self.game_pth).joinpath("unren_cfg.rpy").resolve()
        if not outfile.exists():
            self.make_rpy_cfg(outfile)

        with outfile.open('r+') as ofi:
            for line in ofi:
                if cfg_id in line:
                    self.inf(2, "Option already active. Skipped.")
                    return
            ofi.write(textwrap.dedent(cfg_code))
            self.inf(2, cfg_inf)

    def extract(self):
        """Extracts content from RenPy archives."""
        if UnRen.count["rpa_f_found"] == 0:
            self.inf(0, "Could not find any valid target files in the directory tree.", m_sort='note')

        rkm = self.rpakit.RKmain(self.game_pth, task="exp")
        rkm.cfg_control()
        # TODO: assert success
        self.inf(2, "Extracting of RPA files done.")


    def decompile(self):
        """Decompiles RenPy script files."""
        # TODO: reactivate rpyc decompiler if py3 is supported
        self.inf(0, "For now does `unrpyc` not support python 3! Stay tuned for news on this.", m_sort='warn')
    #     if UnRen.count["rpyc_f_found"] == 0:
    #         self.inf(0, "Could not find any valid target files in the directory tree.", m_sort='note')
    #     unrpyc.decompile_rpyc(game_pth)
    #     self.inf(2, "Decompling of rpyc files done.")

    def console(self):
        """Enables the RenPy console and developer menu."""
        console_id = "# Developer menu and console"
        console_code = """
            # ### Developer menu and console ###
                config.developer = True
                config.console = True
        """
        console_inf = "Added access to developer menu and debug console with the \
                      following keybindings:\nConsole: SHIFT+O\nDev Menu: SHIFT+D"
        self.write_rpy_cfg(console_id, console_code, console_inf)

    def quick(self):
        """Enable Quick Save and Quick Load."""
        quick_id = "# Quick save and load"
        quick_code = """
            # ### Quick save and load ###
                try:
                    config.underlay[0].keymap['quickLoad'] = QuickLoad()
                    config.keymap['quickLoad'] = 'K_F5'
                    config.underlay[0].keymap['quickSave'] = QuickSave()
                    config.keymap['quickSave'] = 'K_F9'
                except:
                    print("Error: Quicksave/-load not working.")
        """
        quick_inf = "Added Quick load, -save with the following keybindings:\
                    \nQuick Save: F5\nQuick Load: F9"
        self.write_rpy_cfg(quick_id, quick_code, quick_inf)

    def skip(self):
        """Enables skipping of unseen content."""
        skip_id = "# Skipping"
        skip_code = """
            # ### Skipping ###
                _preferences.skip_unseen = True
                renpy.game.preferences.skip_unseen = True
                renpy.config.allow_skipping = True
                renpy.config.fast_skipping = True
        """
        skip_inf = "Added the abbility to skip all text using TAB and CTRL keys."
        self.write_rpy_cfg(skip_id, skip_code, skip_inf)

    def rollback(self):
        """Enable rollback fuctionality."""
        rollback_id = "# Rollback"
        rollback_code = """
            # ### Rollback ###
                renpy.config.rollback_enabled = True
                renpy.config.hard_rollback_limit = 256
                renpy.config.rollback_length = 256

                def unren_noblock( *args, **kwargs ):
                    return
                renpy.block_rollback = unren_noblock

                try:
                    config.keymap['rollback'] = [ 'K_PAGEUP', 'repeat_K_PAGEUP', 'K_AC_BACK', 'mousedown_4' ]
                except:
                    print("Error: Rollback not working.")
        """
        rollback_inf = "Rollback with use of the mousewheel is now activated."
        self.write_rpy_cfg(rollback_id, rollback_code, rollback_inf)

    def all_opts(self):
        """Runs all available options."""
        self.extract()
        self.decompile()
        self.console()
        self.quick()
        self.skip()
        self.rollback()
        self.inf(2, "All requested options finished.")

    def _exit(self):
        # TODO: perhaps deleting the tempdir tree without shutil
        shutil.rmtree(self.ur_tmp_dir)
        if not pt(self.ur_tmp_dir).is_dir():
            self.inf(1, "Tempdir was successful removed.")
        else:
            self.inf(0, f"Tempdir {self.ur_tmp_dir} could not be removed!", m_sort='warn')

        self.inf(0, "Exiting UnRen by user request.")
        sys.exit(0)

    def main_menu(self):
        """Displays a console text menu and allows choices from the available options."""
        while True:
            print(f"\n\n{UnRen.menu_screen}\n\n")
            userinp = input("Type the corresponding key character to the task you want to execute: ").lower()
            # FIXME: keyerror on empty str (enter key)
            if any(char not in UnRen.menu_opts.keys() for char in userinp):
                self.inf(0, "\nInvalid key used. Try again.", m_sort='note')
                continue
            break
        self.inf(1, f"Input is valid. Continuing with {UnRen.menu_opts[userinp]} ...")

        meth_call = getattr(self, UnRen.menu_opts[userinp])
        meth_call()
        self.main_menu()

    def toolstream_handler(self):
        """Loads and unpacks the stream to usable source state in a tempdir."""

        store = pickle.loads(base64.b85decode(_TOOLSTREAM))
    	# NOTE: tempdir must be deleted by user or stays e.g. shutil.rmtree(pth)
        self.ur_tmp_dir = tempfile.mkdtemp(prefix='UnRen.', suffix='.tmp')

        for rel_fp, f_data in store.items():
            f_pth = pt(self.ur_tmp_dir).joinpath(rel_fp)
            f_pth.parent.mkdir(parents=True, exist_ok=True)

            with f_pth.open('wb') as ofi:
                ofi.write(f_data)
        # control print
        return self.ur_tmp_dir

    def find_valid_files(self):
        """Determines if rpa and rpyc files are present in the gamedir."""

        for fln in self.game_pth.rglob("*"):
            if fln.suffix in ['.rpa', '.rpi']:
                # RPA_LST.append(fln)
                UnRen.count["rpa_f_found"] += 1
            elif fln.suffix in ['.rpyc', '.rpymc']:
                # RPYC_LST.append(fln)
                UnRen.count["rpyc_f_found"] += 1

    def path_check(self):
        """Path work like location checks."""
        # NOTE: There should be better location checks. And if we use the batch/RenPy
        # python there must be changes in here

        if not self.in_pth:
            script_dir = pt(__file__).resolve().parent
        script_dir = pt(self.in_pth)
        # control print
        print(f"script {script_dir}")
        print(f"cwd {os.getcwd()}")

        if script_dir.joinpath("lib").is_dir() and script_dir.joinpath("renpy").is_dir():
            self.base_pth = script_dir
            # control print
            print(f"script_dir is base")
        elif script_dir.name == "game" and pt(script_dir).joinpath("cache").is_dir():
            self.base_pth = script_dir.parent
            # control print
            print(f"script_dir is game")
        else:
            raise FileNotFoundError(f"Unren is not located in the correct directory! \
                                    Current dir is {script_dir}.")
        # control print
        print(f"script_dir: {script_dir}  -  BASE: {self.base_pth} type: {type(self.base_pth)}")

        self.game_pth = self.base_pth.joinpath("game")


def parse_args():
    """Provides argument parsing functionality on CLI. Obviously."""
    aps = argparse.ArgumentParser(description="A app which provides different functions for the works with RenPy files.", epilog="")
    aps.add_argument('targetpath',
                     action="store",
                     type=str,
                     help="Base path of the target game to work with.")
    aps.add_argument('--verbose',
                     metavar='level [0-2]',
                     type=int,
                     choices=range(0, 3),
                     help='Amount of info output. 0:none, 2:much, default:1')
    aps.add_argument('--version',
                     action='version',
                     version=f'%(prog)s : { __title__} {__version__}')
    return aps.parse_args()


def ur_main(cfg):
    """This executes all program steps, validity checks on the args and prints
    self.infos messages if the default args are used.
    """
    _ur = UnRen(target=cfg.targetpath, verbose=cfg.verbose)

    _ur.path_check()
    _ur.find_valid_files()
    # control print var assignm. can go
    ur_tmp_d = _ur.toolstream_handler()
    _ur.import_tools()
    # # control print testing if tools in temp
    for item in pt(ur_tmp_d).iterdir():
        print(item)
    _ur.main_menu()

    print("\nMain function completed! This should not happen.\n")


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise f"Must be executed in Python 3.6 or later. You are running {sys.version}"
    ur_main(parse_args())
