import os
import sys

"""
This document contains useful micropython code and tricks.

It also contains information about tools to interact with micropython.

In general the micropython docs are your friend: https://docs.micropython.org/en/latest/

Micropython Idle (REPL):
I will use putty for this, but you can use any terminal emulator program (like picocom and minicom on linux).
Open putty and click on 'Session' which should be the upmost option on the left.
Then select 'Serial' on the 'Connection type:' on the right.
Fill in your devices serial line, like: COM3 and the speed, which is: 115200.
Click 'open' on the bottom and click EN (soft reset) on the board.
After a few startup lines the prompt (>>>) should appear and you should be good to go.


pyboard.py
### The following should not be necessary anymore from micropython 1.16 onwards ###
# Startup for the pyboard.py commands:
# On initial connect the board will not listen on the serial interface.
# To activate this call the pyboard.py utility on the right port:
#     D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3
# and press the EN (soft reset) button on board while the program runs.
# The board will reset and after a while the command prompt will pop up (but will take no inputs).
# Control + C out of the program and run whatever you want.

pyboard.py commands:
The pyboard.py utility works for every board.
The filesystem understands common commands like cp, rm, mkdir, rmdir, ls.
You cannot copy into relative paths on the board. All paths are build from /.
Every directory must be created before copying into it.

Print file contents:
    D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3 -f cat boot.py
Run (not copying, just running) a file on the board:
    D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3 boot.py
List directory contents:
    D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3 -f /
Make directory (rmdir for removing):
    D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3 -f mkdir lh_lib
Copy (and overwrite) file (both full/relative paths must be provided, relative path on micropython defaults to root directory):
    D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3 -f cp lh_lib/logging.py :lh_lib/logging.py
Remove file:
    D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3 -f rm lh_lib/logging.py


mpremote
This is the new tool which shall replace pyboard completely at some point.
It offers a combined repl, pyboard and filesystem functionality.
It comes with the repository in /tools, but is also installable via pip: pip install mpremote

mpremote called with no arguments connects to the repl of a currently via usb connected board.
! The exit key combination "STRG and ]" is false for non US/GB keyboard layouts ! -> GER -> "STRG and +"

mpremote currently offers no -help.
Current commands taken from the pypi page( https://pypi.org/project/mpremote/ ):

mpremote connect <device>        -- connect to given device
                                    device may be: list, auto, id:x, port:x
                                    or any valid device name/path
mpremote disconnect              -- disconnect current device
mpremote mount <local-dir>       -- mount local directory on device
mpremote eval <string>           -- evaluate and print the string
mpremote exec <string>           -- execute the string
mpremote run <file>              -- run the given local script
mpremote fs <command> <args...>  -- execute filesystem commands on the device
                                    command may be: cat, ls, cp, rm, mkdir, rmdir
                                    use ":" as a prefix to specify a file on the device
mpremote repl                    -- enter REPL
                                    options:
                                        --capture <file>
                                        --inject-code <string>
                                        --inject-file <file>


mpy-cross
This script offers pre-compile functionality.
It will be built and preconfigured when building micropython from scratch -> git source.
There is a simpler alternative, pip offers it: pip install mpy-cross
The following is tested with the pip module.

mpy-cross offers the following help:
usage: c:\python37\lib\site-packages\mpy_cross\mpy-cross.exe [<opts>] [-X <implopt>] <input filename>
Options:
--version : show version information
-o : output file for compiled bytecode (defaults to input with .mpy extension)
-s : source filename to embed in the compiled bytecode (defaults to input file)
-v : verbose (trace various operations); can be multiple
-O[N] : apply bytecode optimizations of level N

Target specific options:
-msmall-int-bits=number : set the maximum bits used to encode a small-int
-mno-unicode : don't support unicode in compiled strings
-mcache-lookup-bc : cache map lookups in the bytecode
-march=<arch> : set architecture for native emitter; x86, x64, armv6, armv7m, armv7em, armv7emsp, armv7emdp, xtensa, xtensawin

Implementation specific options:
  emit={bytecode,native,viper} -- set the default code emitter
  heapsize=<n> -- set the heap size for the GC (default 2097152)

The following works for my current setup (information gathered by running this information.py script):
mpy-cross -march=xtensawin -X emit=bytecode boot.py
(-X emit=bytecode could be emitted because this is the default)
mpy-cross -march=xtensawin -X emit=native boot.py

Why should you do this?
bytecode mainly reduces the file size which allows for a more compact deployment.
native produces machine code which also includes the micropython overhead. This results in approximately twice the speed
in execution, but it also significantly increases the file size.

todo: The benefits of native code are to be tested!!!

"""

# preferred way of checking if on micropython platform
RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

# get stats about the filesystem (free, used, sizeof blocks)
print("filesystem check:")
print(os.statvfs('/'))
print()

# get mpy compile information
print(".mpy compilation information")
sys_mpy = sys.implementation.mpy
arch = [None, 'x86', 'x64',
    'armv6', 'armv6m', 'armv7m', 'armv7em', 'armv7emsp', 'armv7emdp',
    'xtensa', 'xtensawin'][sys_mpy >> 10]
print('mpy version:', sys_mpy & 0xff)
print('mpy flags:', end='')
if arch:
    print(' -march=' + arch, end='')
if sys_mpy & 0x100:
    print(' -mcache-lookup-bc', end='')
if not sys_mpy & 0x200:
    print(' -mno-unicode', end='')
print()
