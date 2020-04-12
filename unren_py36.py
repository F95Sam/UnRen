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


def import_tools():
    """This runs a deferred import of the tools due to the tools just usable after our script runs already."""
    global rpakit
    try:
        sys.path.append(UR_TMP_DIR)
        # import rpakit
        rpakit = __import__('rpakit', globals(), locals())

        # WARNING: Dont try to import unrpyc. Its py2 only for now.
        # import unrpyc
    except ImportError:
        raise ImportError("Unable to import the tools from temp directory.")


 # Subject to change; thats experimental...hm another placeholder?
with open("version.txt", 'r') as _ofi:
    VER_TXT = _ofi.readline().strip()

__title__ = 'UnRen'
__license__ = 'Apache-2'
__author__ = 'F95sam, madeddy'
__status__ = 'Development'
__version__ = VER_TXT


VERBOSITY = 1
BASE_PTH = None
GAME_PTH = None
UR_TMP_DIR = None
rpa_f_found = False
rpyc_f_found = False
rpakit = None


_TOOLSTREAM = r"_placeholder"


# TODO: Complete and test inf functionality
def inf(inf_level, msg, m_sort=None):
    """Outputs by the current verboseness level allowed infos."""
    if VERBOSITY >= inf_level:  # self.tty ?
        ind1 = f"{__title__}:\x1b[32m >> \x1b[0m"
        ind2 = " " * 10
        if m_sort == 'note':
            ind1 = f"{__title__}:\x1b[93m NOTE \x1b[0m> "
            ind2 = " " * 13
        elif m_sort == 'warn':
            ind1 = f"{__title__}:\x1b[31m WARNING \x1b[0m> "
            ind2 = " " * 17
        print(textwrap.fill(msg, width=90, initial_indent=ind1, subsequent_indent=ind2, replace_whitespace=False))


def write_to_file(cfg_txt):
    """Writes given text to the file."""
    outfile = pt(GAME_PTH).joinpath("unren_cfg.rpy").resolve()
    if not outfile.exists():
        header_txt = """\
            # RenPy script file
            # Config changes; written by UnRen

            init 999 python:
        """
        with outfile.open('a+') as ofi:
            print(textwrap.dedent(header_txt), file=ofi)

    # TODO: Add check if tasks txt already in the cfg file(prevent doubles)
    with outfile.open('a+') as ofi:
        print(textwrap.dedent(cfg_txt), file=ofi)


def extract():
    """Extracts content from RenPy archives."""
    if not rpa_f_found:
        inf(0, "Could not find any valid target files in the directory tree.", m_sort='note')

    rkm = rpakit.RKmain(GAME_PTH, task="exp")
    rkm.cfg_control()


def decompile():
    """Decompiles RenPy script files."""
    inf(0, "For now does `unrpyc` not support python 3! Stay tuned for news on this.", m_sort='warn')
#     if not RPYC_F_FOUND:
#         inf(0, "Could not find any valid target files in the directory tree.", m_sort='note')
    # TODO: reactivate rpyc decompiler if py3 support
#     unrpyc.decompile_rpyc(GAME_PTH)


def console():
    """Enables the RenPy console and developer menu."""
    console_txt = """
        # ### Developer menu and console ###
            config.developer = True
            config.console = True
    """
    write_to_file(console_txt)
    inf(2, "Added access to developer menu and debug console with the \
        following keybindings:\
        \nConsole: SHIFT+O\nDev Menu: SHIFT+D")


def quick():
    """Enable Quick Save and Quick Load."""
    quick_txt = """
        # ### Quick save and load ###
            try:
                config.underlay[0].keymap['quickLoad'] = QuickLoad()
                config.keymap['quickLoad'] = 'K_F5'
                config.underlay[0].keymap['quickSave'] = QuickSave()
                config.keymap['quickSave'] = 'K_F9'
            except:
                print("Error: Quicksave/-load not working.")
    """
    write_to_file(quick_txt)
    inf(2, "Added Quick load, -save with the following keybindings:\
        \nQuick Save: F5\nQuick Load: F9")


def skip():
    """Enables skipping of unseen content."""
    skip_txt = """
        # ### Skipping ###
            _preferences.skip_unseen = True
            renpy.game.preferences.skip_unseen = True
            renpy.config.allow_skipping = True
            renpy.config.fast_skipping = True
    """
    write_to_file(skip_txt)
    inf(2, "Added the abbility to skip all text using TAB and CTRL keys.")


def rollback():
    """Enable rollback fuctionality."""
    rollback_txt = """
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
    write_to_file(rollback_txt)
    inf(2, "Rollback with the scrollwheel is now activated.")


def all_opts():
    """Runs all available options."""
    extract()
    decompile()
    console()
    quick()
    skip()
    rollback()
    inf(2, "All requested options finished.")


def _exit():
    # TODO: Cleanup... and perhaps deleting the tempdir tree without shutil
    shutil.rmtree(UR_TMP_DIR)
    if not pt(UR_TMP_DIR).is_dir():
        inf(1, "Tempdir was successful removed.")
    else:
        inf(0, f"Tempdir {UR_TMP_DIR} could not be removed!", m_sort='warn')

    inf(0, "\nExiting by user request.")
    sys.exit(0)


def main_menu():
    """Displays a console text menu and allows choices from the available options."""
    # IDEA: vars with static nature could be moved into global scope
    valid_chars = ['1', '2', '3', '4', '5', '6', '0', 'x']
    menu_opts = {'1': extract,
                 '2': decompile,
                 '3': console,
                 '4': quick,
                 '5': skip,
                 '6': rollback,
                 '0': all_opts,
                 'x': _exit}
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

    while True:
        print(f"\n\n{menu_screen}\n\n")
        userinp = input("Type the corresponding key character to the task you want to execute: ").lower()
        if any(char not in valid_chars for char in userinp):
            inf(0, "Invalid key used. Try again.", m_sort='note')
            continue
        break
    inf(1, "Input is valid. Continuing...")
    menu_opts[userinp]()
    main_menu()


def toolstream_handler():
    """Loads and unpacks the stream to usable source state in a tempdir."""

    store = pickle.loads(base64.b85decode(_TOOLSTREAM))
	# NOTE: tempdir must be deleted by user or stays e.g. shutil.rmtree(pth)
    ur_tmp_d = tempfile.mkdtemp(prefix='UnRen.', suffix='.tmp')

    for rel_fp, f_data in store.items():
        f_pth = pt(ur_tmp_d).joinpath(rel_fp)
        f_pth.parent.mkdir(parents=True, exist_ok=True)

        with f_pth.open('wb') as ofi:
            ofi.write(f_data)

    return ur_tmp_d


def list_target_files():
    """Determines if rpa and rpyc files are present in the gamedir."""
    global rpa_f_found, rpyc_f_found
    for fln in GAME_PTH.rglob("*"):
        if fln.suffix in ['.rpa', '.rpi']:
            # RPA_LST.append(fln)
            rpa_f_found = True
        elif fln.suffix in ['.rpyc', '.rpymc']:
            # RPYC_LST.append(fln)
            rpyc_f_found = True


def path_check(targetpath):
    """Path work like location checks."""
    # NOTE: There should be better location checks. And more...
    script_dir = pt(__file__).resolve().parent
    if targetpath:
        script_dir = pt(targetpath)
    # control print
    print(f"script {script_dir}")
    print(f"cwd {os.getcwd()}")

    if script_dir.joinpath("lib").is_dir() and script_dir.joinpath("renpy").is_dir():
        b_pth = script_dir
        # control print
        print(f"script_dir is base")
    elif script_dir.name == "game" and pt(script_dir).joinpath("cache").is_dir():
        b_pth = script_dir.parent
        # control print
        print(f"script_dir is game")
    else:
        raise FileNotFoundError(f"Unren is not located in the correct directory! \
                                Current dir is {script_dir}.")
    # control print
    print(f"script_dir: {script_dir}  -  BASE: {BASE_PTH} type: {type(BASE_PTH)}")

    g_pth = b_pth.joinpath("game")

    return b_pth, g_pth


def parse_args():
    """Provides argument parsing functionality on CLI. Obviously."""
    aps = argparse.ArgumentParser(description="A app which provides different functions for the works with RenPy files.", epilog="")
    aps.add_argument("targetpath",
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
    infos messages if the default args are used.
    """
    global UR_TMP_DIR, BASE_PTH, GAME_PTH, VERBOSITY
    if cfg.verbose:
        VERBOSITY = cfg.verbose

    targetpath = pt('')
    if cfg.targetpath:
        targetpath = pt(cfg.targetpath)

    BASE_PTH, GAME_PTH = path_check(targetpath)
    print(GAME_PTH)

    list_target_files()
    UR_TMP_DIR = toolstream_handler()
    import_tools()
    # testing if tools in temp
    for item in pt(UR_TMP_DIR).iterdir():
        print(item)
    main_menu()


    print("\nMain completed!\n")


if __name__ == '__main__':
    if not sys.version_info >= (3, 6):
        raise f"Must be executed in Python 3.6 or later. You are running {sys.version}"
    ur_main(parse_args())
