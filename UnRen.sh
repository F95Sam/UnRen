#!/bin/bash
# Rather dumb imho to exec this as shell and then py, if we can do direct py








version="0.5.0-alpha"
title="UnRen for Linux and Mac v$version"
echo -ne "\e[8;0;90t"


path_check() {
    base_pth=$(cd `dirname $0` && pwd)

    if [ -d "game" ] && [ -d "lib" ] && [ -d "renpy" ]; then
        py_check
    elif [ -d "../game" ] && [ -d "../lib" ] && [ -d "../renpy" ]; then
        base_pth=$(cd `dirname $base_pth` && pwd)
        py_check
    else
        echo "Error: The location of UnRen appears to be wrong. It should
              be in the game's base directory.
              (dirs 'game', 'lib', 'renpy' are present)"
        error
    fi
}


py_check() {
    os_arch=$(uname -m)
    
    if [ *"x64"* in $os_arch ]; then
        python_pth=$base_pth"/lib/linux-x86_64"
    elif [ *"i686"* in $os_arch ]; then
        python_pth=$base_pth"/lib/linux-i686"
    else
        echo "Could not identify OS architecture to set python." 
        error
    fi

    if [ -f $python_pth"/python" ]; then
        echo "python found"
    else
        echo "Error: Cannot locate python, unable to continue.
              Is the correct python version for your computer in the
              $base_pth/lib directory?"
        error
    fi
}


# Python, lets go
run_py() {
    # Did not work: The whole py-path/-home/environment needs be configured -> Nonsense for lx and mac where py runs already
    # NOTE: with switch -E it works so far without setting some py path vars
    $python_pth"/python -EOO" <<EOF
    _placeholder
EOF
}


end() {
    echo "Regular program exit."
    exit 0
}


error() {
    echo "A error occured!" 
    echo "Terminating."
    exit 1
}


path_check
run_py
end
