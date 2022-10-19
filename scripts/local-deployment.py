"""
This script deploys lh_lib onto a connected microcontroller.
This script must be run on the host device.

Used tools:
mpy-cross (installable with: pip install mpy-cross)
mpremote (installable with: pip install mpremote)


To deploy the firmware (micropython) itself on the esp32 controller there are some steps to do beforehand:
* make sure you have a recent python 3 installation (preferably with scripts added to path)
* install the esptool with pip:
pip install esptool
* download the latest GENERIC stable build from here: https://micropython.org/download/esp32/
+ find out on which
* on executing the following commands with esptool: hold the boot button while esptool is connecting
* if the esp32 is new with no prior micropython on it erase the flash with this command (replace COM3 with your usb port):
esptool.py --chip esp32 --port COM3 erase_flash
* deploy the the micropython with this command: (replace COM3 and .bin with your information)
esptool.py --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 esp32-20210618-v1.16.bin

"""
import os
import pathlib
import shutil
import subprocess
import sys
import json

FIRST_DEPLOYMENT = True  # if set, copies boot.py, main.py and wlan.json onto the device (!!! make sure there is a hostname set in wlan.json and that there is at least one pair of valid credentials set (ssid -> pw) !!!)
DEPLOY_BASE_ONLY = False  # if set, deploys only the base module with the base_worker

PRE_COMPILE = True  # Pre-compiles files to .mpy format
NATIVE_CODE = False  # True currently not usable. Uses to much RAM on device. Alternative: use the @micropython.native function decorator
MPY_MARCH = 'xtensawin'  # ESP32

if sys.implementation.name == 'micropython':
    raise Exception("Call this script on a host platform with your microcontroller connected! (python local-deployment.py)")


"""
Utility Classes
"""


class Flags:

    def __init__(self):
        p = subprocess.run(['mpremote', 'fs', 'cp', ':flags.json', 'build/flags.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if p.returncode != 0:
            print("could not retrieve flags.json. creating new one.")
            self.old_flags = {}
        else:
            print("using existing flags.json for reference.")
            with open('build/flags.json', 'r') as f:
                self.old_flags = json.load(f)

    def flags_match(self):
        try:
            return self.old_flags['PRE_COMPILE'] == PRE_COMPILE and self.old_flags['NATIVE_CODE'] == NATIVE_CODE and self.old_flags['MPY_MARCH'] == MPY_MARCH
        except KeyError:
            return False

    @classmethod
    def save_to_device(cls):
        print('saving new build/flags.json to device :flags.json')
        with open('build/flags.json', 'w') as f:
            json.dump({'PRE_COMPILE': PRE_COMPILE, 'NATIVE_CODE': NATIVE_CODE, 'MPY_MARCH': MPY_MARCH}, f)
        subprocess.run(['mpremote', 'fs', 'cp', 'build/flags.json', ':flags.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)


class MTimes:

    def __init__(self):
        self.struct = {}

    def get_m_time(self, fp_parts):
        try:
            sec = self.struct
            for part in fp_parts:
                sec = sec[part]
        except KeyError:
            return 0
        return sec

    def add(self, fp, m_time):
        parts = pathlib.Path(fp).parts
        sec = self.struct
        for part in parts[:-1]:
            if part not in sec:
                sec[part] = {}
            sec = sec[part]
        sec[parts[-1]] = m_time

    def serialize(self):
        return json.dumps(self.struct)

    def as_list(self):
        return self._as_list(self.struct)

    def _as_list(self, root):
        if not isinstance(root, dict):
            return [[]]

        result = []
        for k in root:
            for fp_list in self._as_list(root[k]):
                result.append([k] + fp_list)
        return result

    def load_from_device(self):
        p = subprocess.run(['mpremote', 'fs', 'cp', ':m_times.json', 'build/m_times.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if p.returncode != 0:
            print("could not retrieve device m_times.json. creating new one.")
        else:
            print("using existing m_times.json for reference.")
            with open('build/m_times.json', 'r') as f:
                self.struct = json.load(f)

    def save_to_device(self):
        print(f'saving new build/m_times.json to device :m_times.json')
        with open('build/m_times.json', 'w') as f:
            json.dump(self.struct['build'], f)  # we want struct relative to lh_lib
        subprocess.run(['mpremote', 'fs', 'cp', f'build/m_times.json', f':m_times.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)


"""
Device Code
  
  removes ghost files/directories and creates new directories directly on the device
  
"""
DEVICE_CODE = """

import json
import os

class MTimes:

    def __init__(self, serialized_mtimes=None):
        self.struct = {} if serialized_mtimes is None else json.loads(serialized_mtimes)

    def contains(self, fp_parts):
        return self.get_m_time(fp_parts) != 0

    def get_m_time(self, fp_parts):
        try:
            sec = self.struct
            for part in fp_parts:
                sec = sec[part]
        except KeyError:
            return 0
        return sec

    def as_list(self):
        return self._as_list(self.struct)

    def _as_list(self, root):
        if not isinstance(root, dict):
            return [[]]

        result = []
        for k in root:
            for fp_list in self._as_list(root[k]):
                result.append([k] + fp_list)
        return result
        

# loading mtimes
try:
    with open('m_times.json') as f:
        device_mtimes = MTimes(f.read())
except OSError:
    device_mtimes = MTimes()

build_mtimes = MTimes(SERIALIZED_BUILD_MTIMES)

# removing old files
for parts in device_mtimes.as_list():
    if not build_mtimes.contains(['build'] + parts):
        fp = '/'.join(parts)
        print(f'removing ghost file {fp}')
        try:
            os.remove(fp)
        except OSError:
            print(f'ghost file {fp} does not exist on filesystem. ignoring.')

        dir_parts = parts[:-1]
        while len(dir_parts) > 0:
            directory = '/'.join(dir_parts)
            try:
                if os.listdir(directory):
                    # non empty directory
                    break
                else:
                    # empty directory
                    print(f'removing ghost directory {directory}')
                    os.rmdir(directory)
            except OSError:
                # non existent directory
                break
            dir_parts = parts[:-1]

# create directories if they do not exist
try:
    os.stat('lh_lib')
except OSError:
    print(f'creating non existent directory lh_lib on device')
    os.mkdir('lh_lib')

unique_directories = []
for parts in build_mtimes.as_list():
    directory = '/'.join(parts[1:-1])  # first part is 'build' and last part is "filename"
    if directory not in unique_directories:
        unique_directories.append(directory)

for directory in unique_directories:
    parts = directory.split('/')
    partial_directory = ''
    
    while len(parts)>0:
        partial_directory += '/' + parts.pop(0)

        try:
            os.stat(partial_directory)
        except OSError:
            print(f'creating non existent directory {partial_directory} on device')
            os.mkdir(partial_directory)
"""


if __name__ == '__main__':
    # set working directory to repository root for the case that the script is not called in its directory
    os.chdir(os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    print(f'changed working directory to: {os.getcwd()}')

    # check if device is reachable
    print('checking device access (with "mpremote fs ls")...', end='', flush=True)
    subprocess.run(['mpremote', 'fs', 'ls'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
    print('check')

    # remove old build directory
    print('removing old build directory')
    shutil.rmtree('build')

    # create new build_m_times
    build_mtimes = MTimes()

    # build files
    if not os.path.isdir('build'):
        os.mkdir('build')

    directory_to_deploy = 'lh_lib/base' if DEPLOY_BASE_ONLY else 'lh_lib'

    for path, _, files in os.walk(directory_to_deploy):
        for file in files:
            if file.endswith('.py'):
                lib_fp = os.path.join(path, file)
                out_fp_noext, lib_ext = os.path.splitext(os.path.join('build', lib_fp))
                out_ext = '.mpy' if PRE_COMPILE else '.py'
                out_fp = out_fp_noext + out_ext

                # mpy-cross silently fails on non-existent sub-directories, so lets ensure we have them
                if not os.path.isdir(os.path.dirname(out_fp)):
                    os.makedirs(os.path.dirname(out_fp))

                if PRE_COMPILE:
                    print(f'compiling file {lib_fp} to {out_fp}')
                    subprocess.run(['mpy-cross', '-o', out_fp, f'-march={MPY_MARCH}', '-X', f'emit={"native" if NATIVE_CODE else "bytecode"}', lib_fp], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
                else:
                    print(f'copying file {lib_fp} to {out_fp}')
                    shutil.copy2(lib_fp, out_fp)

                build_mtimes.add(out_fp, int(os.stat(lib_fp).st_mtime))  # using int cast, because esp32 float precision cannot handle this long float

    # get device_m_times
    device_mtimes = MTimes()
    device_mtimes.load_from_device()

    # get device flags
    device_flags = Flags()

    # run device code to remove ghost files/directories and create new directories
    code_to_execute = f"SERIALIZED_BUILD_MTIMES='{build_mtimes.serialize()}'\n{DEVICE_CODE}"
    subprocess.run(['mpremote', 'exec', code_to_execute], check=True)

    # deploy modified and new files
    for parts in build_mtimes.as_list():
        src_fp = '/'.join(parts)
        dst_fp = '/'.join(parts[1:])
        if not device_flags.flags_match() or build_mtimes.get_m_time(parts) > device_mtimes.get_m_time(parts[1:]):
            print(f'copying host file {src_fp} to device :{dst_fp}')
            subprocess.run(['mpremote', 'fs', 'cp', src_fp, f':{dst_fp}'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

    device_flags.save_to_device()
    build_mtimes.save_to_device()

    if FIRST_DEPLOYMENT:
        print('copying additional files of first deployment:')
        print('copying host file wlan.json to device :wlan.json')
        subprocess.run(['mpremote', 'fs', 'cp', 'wlan.json', ':wlan.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
        print('copying host file boot.py to device :boot.py')
        subprocess.run(['mpremote', 'fs', 'cp', 'boot.py', ':boot.py'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
        print('copying host file main.py to device :main.py')
        subprocess.run(['mpremote', 'fs', 'cp', 'main.py', ':main.py'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
