import uos

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
"""

# get stats about the filesystem (free, used, sizeof blocks)
print(uos.statvfs('/'))
