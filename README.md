# Bachelor Thesis
This is the software archive for my bachelor thesis.

# The Code Structure
The archive has a lh_lib directory, version directories and general scripts
## lh_lib
This contains the actual framework code. The deployment script transfers this code onto esp32 controllers.
Examples on how to start the framework are the vfinal/run-desktop-worker.py and the vfinal/run-micropython-worker.py.
The vfinal/run-micropython-worker.py script must be run on the esp32 with for 
example: mpremote run vfinal/run-micropython-worker.py
## vfinal
Contains code to start the framework and utility scripts for the case study
### vfinal/case_studies
contains the code to generate the case study computational setup and assignments
### vfinal/assign-case-study.py
utility script to clear or assign case study assignments
### vfinal/convert_log_data.py
utility script that generates valid pgfplots data from the raw observables data
### vfinal/example.py
the example computational setup and assignment
### vfinal/filter_delay_cutoffs.py
generates high value cutoff filtered versions for case study 1 and 2 converted delay measurements
### vfinal/run-desktop-worker.py
to be run on a console. starts the framework on a computer
### vfinal/run-micropython-worker.py
to be run on an esp32 with mpremote run ... . Starts the framework on micropython.
### vfinal/start-case-study-pc-instances.ps1
powershell script that starts all computer framework instances needed by the case study assignments.
## boot.py
The boot script that is run on all esp32s in this thesis. The device name is adjusted to the current esp32.
The Wifi credentials for my Wifi are obviously not in this archive. The script must be transferred manually to the
esp32, for example with: mpremote fs cp boot.py :boot.py
## clear-device-filesystem.py
The script must be run on the esp32 and deletes all files in the filesystem on it. This was used as I once corrupted
one esp32s filesystem and could not get the files removed with an external tool (mpremote)
## deployment.py
To be called on the computer with the esp32 running micropython connected. Deploys the lh_lib files onto the esp32
## information.py
Contains useful information about tools like mpy-cross, mpremote. Prints some stats when run on an esp32.
## main.py
NOT THE START SCRIPT FOR THE COMPUTER FRAMEWORK VERSION. 

Only works if transferred manually to the esp32 running
micropython with for example: mpremote fs cp main.py :main.py

Micropython supports two scripts automatically. boot.py is run first as a setup script. main.py is run second for
program logic that should be run on micropython start (which is on poweron, or the EN button)

## possible integration
The device to device communication can be split from the user modules.

Change the programming model so there are only user functions with the already used io model.

The user class model is omitted and the graph is build by using function name strings and the necessary kwargs to run it.

Graph linking is open for suggestions.

Now use rescala and scalaloci to build a distributed function graph.

Now use the student's thesis to convert the individual nodes of the graph into python functions.

Now develop a custom mapper to generate the python-framework understandable json graph structure with these functions.

Now find a way to (dynamically?) distribute the python functions onto the microprocessors.

Now use the python-framework intended way to run the graph.

Now your done and scalaloci can create and distribute a scala reactive graph onto microprocessors.

