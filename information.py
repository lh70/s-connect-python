import os
import sys

"""
In this document I will gather useful python/micropython code, like a cheatsheet.

In addition I will write down the most important commands to interact with micropython and their particularities.

In general the micropython docs are your friend: https://docs.micropython.org/en/latest/

Micropython Idle (REPL):
I will use putty for this, but you can use any terminal emulator program (like picocom and minicom on linux).
Open putty and click on 'Session' which should be the upmost option on the left.
Then select 'Serial' on the 'Connection type:' on the right.
Fill in your devices serial line, like: COM3 and the speed, which is: 115200.
Click 'open' on the bottom and click EN (soft reset) on the board.
After a few startup lines the prompt (>>>) should appear and you should be good to go.

Startup for the pyboard.py commands:
On initial connect the board will not listen on the serial interface.
To activate this call the pyboard.py utility on the right port:
    D:/Data/Benutzer/Lukas/PyCharmProjects/micropython/micropython/tools/pyboard.py -d COM3
and press the EN (soft reset) button on board while the program runs.
The board will reset and after a while the command prompt will pop up (but will take no inputs).
Control + C out of the program and run whatever you want.

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
Copy (and overwrite) file:
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
