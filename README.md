# Dev branch
At the moment **this is the development branch** for the python rewrite of the
_UnRen application._
> **Do not use for productive work!**

The following content is just a raw outline of the current project state respectively
development plans and subject to change **at any given time**.

<!-- madeddy: This line and above is to be removed on dev completion -->

# UnRen
Small multifunctional wrapper app around tools for the work with RenPy files.
The features offered include:
- Decompressing RPA files
- Decompiling RenPy script files (rpyc)
- Activating respectively reactivating:
 - Developer menu and console
 - Quick Save and Quick Load
 - Rollback function
 - Text skipping


## Usage
### Console command version for win
Double click to start the app file or open a cmd terminal and execute there for example
```batch
C:\..\your_path\unren27.cmd
```
Alternatively use in the code line `unren36.cmd` if the game needs Python 3.

> Inside the game directory we called above `game_name` must be the directorys
`renpy`, `lib` and a starter file like `your_game_name.(exe|py|sh)`.
e.g. `the_question.py`
If not, you're in the wrong loction!

### Pure python version
We can start the python-only scripts in two ways. Either we use the in your operating
system installed python or the one which comes with your RenPy game.

#### OS python
Just open your systems terminal and use the command line for your use case.
For python 3.6+:
```sh
python3 unren_py36.py ../your_path/game_name/
```
or for python 2.7+:
```sh
python2 unren_py27.py ../your_path/game_name/
```

#### RenPy python
To use the Python distribution which came along your game, the corresponding system
architecture must be selected in the lib folder. Also, if more as one OS available is
the correct OS directory must be considered.
e.g. 
To use **64** Bit on **Linux** and with a Python **3** game:
```
../your_path/game_name/lib/linux-x86_64/python -EOO unren_py37.py ../your_path/game_name/
```
For **32** Bit on **Windows** and with a Python **2** game:
```
../your_path/game_name/lib/windows-i686/python -EOO unren_py27.py ../your_path/game_name/
```


## Project content overview
### _Release version files_
`unren_py36.py` / `unren_py27.py`  
The UnRen main app for py 3.6+ or 2.7 completely in python. Users who want to use
this variant must be able to work with a terminal.
_In progress_

`unren_36.cmd` / `unren_27.cmd`  
A command script wrapper for the UnRen main app for py 3.6+ or 2.7. For users who
want to use one-click start for the app.

### _Internal used project module files_ 

`unren_build.py`  
A helper script who constructs the final release versions from different source
files.
- Step 1: Collects the rpy snippeds and embeds them in the raw python script. Converts
also the tools to a bytestream and embeds them also(+ pickled and base coded).
- Step 2 (optional, just windows): Writes the previously prepaired UnRen python
script in the batch file. 
_In progress_

`ur_base.cmd`  
This Windows command file is planed as the one-click starter for the python main
app. The python code will be embeded so we get a hybrid file.
_Completed_

`ur_embed_36.py` / `ur_embed_27.py`  
The reduced version of the UnRen(py3.6+ / py2.7) for embedding in the batch
script.
_Not started_

`ur_tools/*`  
Contains actual versions of the used third party tools which will be embeddet in
the python script.
_Completed_

`ur_embed_rpy/*`  
The RenPy snippeds with code which will be embeddet in the python script. Also
separately usable by copying simply in the game directory.
_Completed_

`readme.md`  
...the file for the stuff you read just now.

## Contributing
If you want to add something to this project, feel free to fork the UnRen repo
and open a pull request with your addition.

Though not interested in complicating things, we want to set some basic standards:
- Don't make commits and/or pull request to big; separate thematic if possible
- Pure cosmetic changes like corrected typos or formating will not be accepted.
Add these to a valid content addition commit.
- Fill always a self explaining commit message
- If you're unsure if your contribution will be accepted ask beforehand. It's cost
free.



---
_TBD:_
## Legal
### License

### Credits 
