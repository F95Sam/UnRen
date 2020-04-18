# Dev branch
At the moment **this is the development branch** for the python rewrite of the _UnRen application._
> **Do not use for productive work!**

The following content is just a raw outline of the current project state respectively
development plans and subject to change at any given time.

## File overview
`readme.md`

The file for what you read just now...

`unren_py36.py`

The UnRen main app for py 3.6+ in pure python.
_In progress_

`unren_py27.py`

The UnRen main app for py 2.7 in pure python.
_Barely started_

`unren.cmd` / `unren.sh`

The Windows command and Linux/Mac shell files are basicly identical and planed as the
one-click starter for the python main app. The python code will be embeded so we get
hybrid files.

`unren_build.py`

A short helper who converts the tools to a bytestream and embeds it in the unren main
script.(+ pickled and base coded)

`unren_embed_py36.py`

The reduced version of the UnRen(py3.6+) for embedding in the batch/shell scripts. 
_Not started_

`unren_embed_py27.py`

The reduced version of the UnRen(py2.7) for embedding in the batch/shell scripts. 
_Not started_


## Contributing
If you want to add something to this project, feel free to fork the UnRen repo and
open a pull request with your addition.

Though not interested in complicating things, we want to set some basic standards:
- Don't make commits and/or pull request to big; separate thematic if possible
- Pure cosmetic changes like corrected typos or formating will not be accepted.
Add these to a valid content addition commit.
- Fill always a self explaining commit message
- If you're unsure if your contribution will be accepted ask beforehand. It's cost free.

<!-- madeddy: This line and above is to be removed on dev completion -->

# UnRen
Small multifunctional wrapper app around tools for the work with RenPy files.
The features offered include:
- Decompressing RPA files
- Decompiling RenPy script files (rpyc)
- Activating respektive reactivating:
 - Developer menu and console
 - Quick Save and Quick Load
 - Text skipping
 - Rollback function

## Usage
<!-- madeddy: Hm. Will we really need a batch file? -->
### Batch version / Shell version
Double click to start the app or open a cmd _or_ shell terminal and execute there ..\your_path\unren.cmd _or_ ../your_path/unren.sh

### Pure python version
For python 3.6+ use:
```shell
python3 unren_py36.py ../your_path/game_name
```
or for python 2.7+
```shell
python2 unren_py27.py ../your_path/game_name
```


_TBD:_
## Legal
### License

### Credits 
