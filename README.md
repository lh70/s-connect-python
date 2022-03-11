# s(ensor)-connect-python
This is the software archive for the s-connect-python MicroPython framework
, which is based on my bachelor thesis.

# The Code Structure
The archive has a lh_lib directory, version directories and general scripts
## lh_lib
This folder contains the actual framework code. The scripts/deployment.py script transfers this code onto esp32 controllers.
Examples on how to start the framework are the scripts/run-desktop-worker.py and the scripts/run-micropython-worker.py.
The scripts/run-micropython-worker.py script must be run on the esp32 with for 
example: mpremote run vfinal/run-micropython-worker.py
## thesis-resources
Contains code to generate and assign the thesis case studies, as well as utility scripts
to format the gathered data.
### thesis-resources/case_studies
contains the code to generate the case study computational setup and assignments
### thesis-resources/assign-case-study.py
utility script to clear or assign case study assignments
### thesis-resources/convert-log-data.py
utility script that generates valid pgfplots data from the raw observables data
### thesis-resources/example.py
the example computational setup and assignment
### thesis-resources/filter-delay-cutoffs.py
generates high value cutoff filtered versions for case study 1 and 2 converted delay measurements
### thesis-resources/start-case-study-pc-instances.ps1
powershell script that starts all computer framework instances needed by the case study assignments.

## scripts
This folder contains essential scripts.
### scripts/clear-device-filesystem.py
The script must be run on the esp32 and deletes all files in the filesystem on it. This was used as I once corrupted
one esp32s filesystem and could not get the files removed with an external tool (mpremote)
### scripts/deployment.py
To be called on the computer with the esp32 running micropython connected. Deploys the lh_lib files onto the esp32
### scripts/information.py
Contains useful information about tools like mpy-cross, mpremote. Prints some stats when run on an esp32.
### scripts/run-desktop-worker.py
to be run on a console. starts the framework on a computer
### scripts/run-micropython-worker.py
to be run on an esp32 with mpremote run ... . Starts the framework on micropython.

## boot.py
The boot script that is run on all esp32s in this thesis. The device name is adjusted to the current esp32.
Valid Wifi credentials must be added before transferring. The script must be transferred manually to the
esp32, for example with: mpremote fs cp boot.py :boot.py
## main.py
NOT THE START SCRIPT FOR THE COMPUTER FRAMEWORK VERSION. 

The MicroPython main.py script, that gets executed on the esp32's after startup and running boot.py.
Contains basically the same code as scripts/run-micropython-worker.py. Must also be transferred manually onto the esp32,
for example with: mpremote fs cp main.py :main.py
