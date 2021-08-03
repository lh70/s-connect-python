"""
This script deploys lh_lib onto a connected microcontroller.
This script must be run on the host device.

Used tools:
mpy-cross (installable with: pip install mpy-cross)
mpremote (installable with: pip install mpremote)


To deploy the firmware (micropython) itself on the esp32 controller there are some steps to do beforehand:
* install the esptool with pip:
pip install esptool
* download the latest GENERIC stable build from here: https://micropython.org/download/esp32/
* hold the boot button while esptool is connecting on the following commands
* if the esp32 is new with no prior micropython on it erase the flash with this command:
esptool --chip esp32 --port COM3 erase_flash
* deploy the the micropython with this command: (replace port and .bin with your information)
esptool --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 esp32-20210618-v1.16.bin

"""
import json
import pathlib
import os
import sys
import shutil
import subprocess

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'
PRE_COMPILE = True
NATIVE_CODE = False  # True currently not usable. Uses to much RAM on device.
MPY_MARCH = 'xtensawin'


# mpremote only works with unix like forward slashes, so lets enforce these
def os_path_join(*parts):
    def convert(path):
        return path.replace('\\', '/').replace('//', '/')
    return '/'.join(map(convert, parts))


class Flags:

    def __init__(self):
        p = subprocess.run(['mpremote', 'fs', 'cp', ':flags.json', 'build/flags.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if p.returncode is not 0:
            print("could not retrieve flags.json. creating new one.")
            self.old_flags = {}
        else:
            print("using exisiting flags.json for reference.")
            with open('build/flags.json', 'r') as f:
                self.old_flags = json.load(f)

    def flags_match(self):
        try:
            return self.old_flags['PRE_COMPILE'] == PRE_COMPILE and self.old_flags['NATIVE_CODE'] == NATIVE_CODE and self.old_flags['MPY_MARCH'] == MPY_MARCH
        except KeyError:
            return False

    @classmethod
    def save_to_device(cls):
        print('saving new build/flags.json to :flags.json')
        with open('build/flags.json', 'w') as f:
            json.dump({'PRE_COMPILE': PRE_COMPILE, 'NATIVE_CODE': NATIVE_CODE, 'MPY_MARCH': MPY_MARCH}, f)
        subprocess.run(['mpremote', 'fs', 'cp', 'build/flags.json', ':flags.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)


class MTimes:

    def __init__(self, init_struct=None):
        self.struct = init_struct or {}

    def contains(self, fp_parts):
        return self.get_m_time(fp_parts) is not 0

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
        if p.returncode is not 0:
            print("could not retrieve device m_times.json. creating new one.")
        else:
            print("using existing m_times.json for reference.")
            with open('build/m_times.json', 'r') as f:
                self.struct = json.load(f)

    def save_to_device(self):
        print(f'saving file build/m_times.json to device :m_times.json')
        with open('build/m_times.json', 'w') as f:
            json.dump(self.struct['build'], f)  # we want struct relative to lh_lib
        subprocess.run(['mpremote', 'fs', 'cp', f'build/m_times.json', f':m_times.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)


def run():
    if RUNNING_MICROPYTHON:
        raise Exception("Call this script on the host platform with your microcontroller connected! (python deployment.py)")

    # set correct working directory for tha case that the script is not called in its directory
    os.chdir(os.path.realpath(os.path.dirname(__file__)))
    print(f'changed working directory to: {os.getcwd()}')

    # check if device is reachable
    print('checking device access (with "mpremote fs ls")...', end='')
    subprocess.run(['mpremote', 'fs', 'ls'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
    print('check')

    # remove old build directory
    print('removing old build directory')
    shutil.rmtree('build')

    # create new build_m_times
    build_m_times = MTimes()

    # build files
    if not os.path.isdir('build'):
        os.mkdir('build')

    for path, _, files in os.walk('lh_lib'):
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

                build_m_times.add(out_fp, os.stat(lib_fp).st_mtime)

    # get device_m_times
    device_m_times = MTimes()
    device_m_times.load_from_device()

    # get device flags
    device_flags = Flags()

    # delete old files
    for parts in device_m_times.as_list():
        if not build_m_times.contains(['build'] + parts):
            fp = '/'.join(parts)
            print(f'removing ghost file {fp}')
            subprocess.run(['mpremote', 'fs', 'rm', fp], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

            dir_parts = parts[:-1]
            while len(dir_parts) > 0:
                dp = '/'.join(parts)
                p = subprocess.run(['mpremote', 'fs', 'rmdir', dp], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if p.returncode is 0:
                    print(f'removing ghost directory {dp}')
                else:
                    break

    # make directories on device if they do not exist
    process = subprocess.run(['mpremote', 'fs', 'ls', 'lh_lib'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if process.returncode != 0:
        print(f'creating non existent directory lh_lib on device')
        subprocess.run(['mpremote', 'fs', 'mkdir', 'lh_lib'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

    for path, directories, _ in os.walk('build/lh_lib'):
        path = '/'.join(pathlib.Path(path).parts[1:])  # remove build from path
        for directory in directories:
            p = os_path_join(path, directory)

            process = subprocess.run(['mpremote', 'fs', 'ls', p], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if process.returncode != 0:
                print(f'creating non existent directory {p} on device')
                subprocess.run(['mpremote', 'fs', 'mkdir', p], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

    # deploy modified and new files
    for parts in build_m_times.as_list():
        src_fp = '/'.join(parts)
        dst_fp = '/'.join(parts[1:])
        if not device_flags.flags_match() or build_m_times.get_m_time(parts) > device_m_times.get_m_time(parts[1:]):
            print(f'copying host file {src_fp} to device :{dst_fp}')
            subprocess.run(['mpremote', 'fs', 'cp', src_fp, f':{dst_fp}'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

    device_flags.save_to_device()
    build_m_times.save_to_device()


if __name__ == '__main__':
    run()
