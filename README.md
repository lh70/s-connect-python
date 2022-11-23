# s(ensor)-connect-python
This is the software archive for the s-connect-python MicroPython framework
, which is based on my bachelor thesis.

# Quick Guide: First Time Setup
### General Windows/Linux Machines
Clone this repository. Run `python scripts/run-desktop-worker.py`. Done.
### Raspberry Pi
Clone this repository. Run `python scripts/run-raspi-worker.py`. Done.
### ESP32
1. Follow the instructions in the comment of `scripts/deployment.py` to install micropython on the esp32
2. Make sure you installed mpy_cross and mpremote via `pip install mpy-cross` and `pip install mpremote`
3. Check that your esp32 is reachable by calling `mpremote` and thereby entering the repl. Close the commandline again.
   (mpremote can be exited via CTRL +)
4. Run `python scripts/deployment.py` to copy the framework onto the esp32. !!! This will take a while !!!
5. Fill the required information into `wlan.json` and copy it onto the esp32 via `mpremote fs cp wlan.json :wlan.json`.
6. Copy the `boot.py` file onto the esp32 via `mpremote fs cp boot.py :boot.py`.
7. Check that your esp32 connects to wlan by entering the repl (`mpremote`) and pressing the `EN` button on the esp.
8. Check that the framework is runnable by starting it via `mpremote run scripts/run-micropython-worker.py`.
9. (Optional) Copy the `main.py` file onto the esp32 via `mpremote fs cp main.py :main.py`.
This is necessary if you want the framework to be run automatically on esp32 power-on or reset(EN button).
If you need to call scripts/deployment.py again or enter the repl, make sure you stop the framework by entering the
repl via `mpremote` and exit main.py via CTRL c.
10. Done.


# The Code Structure
The archive has a lh_lib directory, version directories and general scripts.
## lh_lib
This folder contains the actual framework code. The scripts/deployment.py script transfers this code onto esp32 controllers.
Examples on how to start the framework are the scripts/run-desktop-worker.py, scripts/run-micropython-worker.py and 
scripts/run-raspi-worker. The scripts/run-micropython-worker.py script must be run on the esp32 with for 
example: mpremote run vfinal/run-micropython-worker.py .
## thesis-resources
Contains code to generate and assign the thesis case studies, as well as utility scripts
to format the gathered data.
### thesis-resources/case_studies
contains the code to generate the case study computational setup and assignments.
### thesis-resources/assign-case-study.py
utility script to clear or assign case study assignments.
### thesis-resources/convert-log-data.py
utility script that generates valid pgfplots data from the raw observables data.
### thesis-resources/example.py
the example computational setup and assignment.
### thesis-resources/filter-delay-cutoffs.py
generates high value cutoff filtered versions for case study 1 and 2 converted delay measurements.
### thesis-resources/start-case-study-pc-instances.ps1
powershell script that starts all computer framework instances needed by the case study assignments.

## scripts
This folder contains essential scripts.
### scripts/clear-device-filesystem.py
The script must be run on the esp32 (mpremote) and deletes all files in the filesystem on it. It can be used to clear a corrupted
filesystem on an esp32.
### scripts/deployment.py
To be called on the computer with the esp32 running micropython connected. Deploys the lh_lib files onto the esp32.
### scripts/information.py
Contains useful information about tools like mpy-cross, mpremote. Prints some stats when run on an esp32.
### scripts/run-desktop-worker.py
to be run on a console. starts the framework on a computer.
### scripts/run-micropython-worker.py
to be run on an esp32 with mpremote run ... . Starts the framework on micropython with all sensors implemented for
esp32 enabled.
### scripts/run-raspi-worker.py
to be run on a raspberry pi. Starts the framework with all sensors implemented for esp32 enabled.

## boot.py
The boot script that is run on all esp32s in this thesis. The device name is adjusted to the current esp32.
Valid Wifi credentials must be added before transferring. The script must be transferred manually to the
esp32, for example with: mpremote fs cp boot.py :boot.py
## main.py
NOT THE START SCRIPT FOR THE COMPUTER FRAMEWORK VERSION. 

The MicroPython main.py script, that gets executed on the esp32's after startup and running boot.py.
Contains the same code as scripts/run-micropython-worker.py. It must be transferred manually onto the esp32,
for example with: mpremote fs cp main.py :main.py


# Notes for later
Instead of using the py_lcd module, maybe port https://github.com/arduino-libraries/LiquidCrystal to micropython.
It seems simple with low overhead.


# natmodule setup
This is a step-by-step guide on how to set up a toolchain to compile c-modules into a .mpy files for ESP32.
1. If you are on Windows, setup wsl, and maybe use `Windows Terminal` (from Windows Store) for easy access/integration.
2. The following is tested on Debian/Ubuntu, but should work on all distros
3. Everything toolchain related will reside in `~/esp`. Feel free to adjust this.
4. `cd ~; mkdir esp; cd esp`
5. `git clone https://github.com/micropython/micropython.git`
6. `cd micropython`
7. `git checkout v1.19.1` replace the version with your currently deployed micropython version, \
or else the module import will fail with `ValueError: incompatible .mpy file`
8. `cd ~`
9. `wget https://github.com/espressif/crosstool-NG/releases/download/esp-2022r1/xtensa-esp32-elf-gcc11_2_0-esp-2022r1-linux-amd64.tar.xz` \
replace link with the current release of `xtensa-esp32-elf` on https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/tools/idf-tools.html#xtensa-esp32-elf
10. `tar -xf xtensa-esp32-elf-gcc11_2_0-esp-2022r1-linux-amd64.tar.xz -C esp` replace tar-file with your downloaded one
11. add `export PATH="$PATH:$HOME/esp/xtensa-esp32-elf/bin"` to your `~/.profile` if you are in a shell. \
you can also manually export the path or make it otherwise available. \
edit `~/.profile` for example with `nano ~/.profile`
12. logout and login or use a new shell
13. place the `minimal example` from https://docs.micropython.org/en/latest/develop/natmod.html#minimal-example in your project
14. replace the following lines in the `Makefile`: \
`MPY_DIR = ../../..` with `MPY_DIR = /home/YOUR_USER_NAME/esp/micropython` !!! `~/` will not work !!!\
`ARCH = x64` with `ARCH = xtensawin`
15. navigate to `.../factorial`. Windows users can navigate to windows-paths via `/mnt/c/...` `/mnt/d/...`
16. `make`
17. copy the .mpy module to your ESP32 and validate via `import factorial` that the version is correct
