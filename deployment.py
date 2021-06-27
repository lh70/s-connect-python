"""
This script deploys lh_lib onto a connected microcontroller.
This script must be run on the host device.

Steps:
1. copy :m_time.json build/m_time.json from device to host.
2. pre-compile or copy files from lh_lib/ to build/lh_lib if lh_lib/ file is newer than corresponding build/lh_lib file.
(if file does not exist in build yet, it will be copied/pre-compiled)
3. make directories on device if they do not exist
4. copy build/lh_lib/ files to :lh_lib onto device if m_time in build/m_time.json is older than m_time of file.
(if file does not exist in m_time.json it will be copied onto device)
(all copied files m_times are saved into a json-tree structure)
5. overwrite build/m_time.json with new m_times-tree-structure. copy build/m_times.json :m_times.json onto device.

Used tools:
mpy-cross (installable with: pip install mpy-cross)
mpremote (installable with: pip install mpremote)
"""
import json
import os
import sys
import shutil
import pathlib
import subprocess

PRE_COMPILE = True
NATIVE_CODE = False
MPY_MARCH = 'xtensawin'

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if RUNNING_MICROPYTHON:
    raise Exception("Call this script on the host platform with your microcontroller connected! (python deployment.py)")


# mpremote only works with unix like forward slashes, so lets enforce these
def os_path_join(*parts):
    def convert(path):
        return path.replace('\\', '/').replace('//', '/')
    return '/'.join(map(convert, parts))


# checks if build file is older than lib file
def build_file_old(lib_fp, out_fp):
    if not os.path.exists(out_fp):
        return True
    return os.stat(lib_fp).st_mtime > os.stat(out_fp).st_mtime


class M_TIMES:

    def __init__(self):
        p = subprocess.run(['mpremote', 'fs', 'cp', ':m_times.json', 'build/m_times.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if p.returncode is not 0:
            print("Could not retrieve m_times.json. Creating new one.")
            self.old_m_times = {}
        else:
            print("Using existing m_times.json for reference.")
            with open('build/m_times.json', 'r') as f:
                self.old_m_times = json.load(f)
        self.new_m_times = {}

    # checks if device file is older than build file
    def device_file_old(self, fp):
        parts = pathlib.Path(fp).parts
        # get old flag
        try:
            sec = self.old_m_times
            for part in parts:
                sec = sec[part]
        except KeyError:
            old_m_time = 0
            is_old = True
        else:
            old_m_time = sec
            is_old = os.stat(fp).st_mtime > sec

        # add correct m_time to new m_times
        new_sec = self.new_m_times
        for part in parts[:-1]:
            if part not in new_sec:
                new_sec[part] = {}
            new_sec = new_sec[part]
        new_sec[parts[-1]] = os.stat(fp).st_mtime if is_old else old_m_time

        return is_old

    def save_new_m_times(self):
        print('saving new build/m_times.json to :m_times.json')
        with open('build/m_times.json', 'w') as f:
            json.dump(self.new_m_times, f)
        subprocess.run(['mpremote', 'fs', 'cp', 'build/m_times.json', ':m_times.json'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)


def run():
    # set correct working directory for tha case that the script is not called in its directory
    os.chdir(os.path.realpath(os.path.dirname(__file__)))
    print(f'changed to working directory: {os.getcwd()}')

    # check if device is reachable
    print('checking device access (with "mpremote fs ls")...', end='')
    subprocess.run(['mpremote', 'fs', 'ls'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
    print('check')

    # create build/ directory if not exists
    if not os.path.isdir('build'):
        os.mkdir('build')

    # step 1: copy m_times.json
    m_times = M_TIMES()

    # step 2: pre-compile / copy
    for path, _, files in os.walk('lh_lib'):
        for file in files:
            if file.endswith('.py'):
                lib_fp = os.path.join(path, file)
                out_fp_noext, lib_ext = os.path.splitext(os.path.join('build', lib_fp))
                out_ext = '.mpy' if PRE_COMPILE else '.py'
                out_fp = out_fp_noext + out_ext

                # remove old build versions of the file
                if out_ext == '.mpy' and os.path.exists(out_fp_noext + '.py'):
                    print(f'removing old build file: {out_fp_noext + ".py"}')
                    os.remove(out_fp_noext + '.py')
                if out_ext == '.py' and os.path.exists(out_fp_noext + '.mpy'):
                    print(f'removing old build file: {out_fp_noext + ".mpy"}')
                    os.remove(out_fp_noext + '.mpy')

                # build file
                if build_file_old(lib_fp, out_fp):
                    # mpy-cross silently fails on non-existent sub-directories
                    if not os.path.isdir(os.path.dirname(out_fp)):
                        os.makedirs(os.path.dirname(out_fp))

                    if PRE_COMPILE:
                        print(f'compiling file {lib_fp} to {out_fp}')
                        subprocess.run(['mpy-cross', '-o', out_fp, f'-march={MPY_MARCH}', '-X', f'emit={"native" if NATIVE_CODE else "bytecode"}', lib_fp], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
                    else:
                        print(f'copying file {lib_fp} to {out_fp}')
                        shutil.copy2(lib_fp, out_fp)

    # change working directory into build directory
    os.chdir('build')

    # step 3: make directories on device if they do not exist
    process = subprocess.run(['mpremote', 'fs', 'ls', 'lh_lib'], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if process.returncode != 0:
        print(f'creating non existent directory lh_lib on device')
        subprocess.run(['mpremote', 'fs', 'mkdir', 'lh_lib'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

    for path, directories, _ in os.walk('lh_lib'):
        for directory in directories:
            p = os_path_join(path, directory)

            process = subprocess.run(['mpremote', 'fs', 'ls', p], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if process.returncode != 0:
                print(f'creating non existent directory {p} on device')
                subprocess.run(['mpremote', 'fs', 'mkdir', p], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

    # step 4: copy build/lh_lib/ files onto device :lh_lib/
    for path, _, files in os.walk('lh_lib'):
        for file in files:
            fp = os_path_join(path, file)

            if m_times.device_file_old(fp):
                print(f'copying host file {fp} to device :{fp}')
                subprocess.run(['mpremote', 'fs', 'cp', fp, f':{fp}'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)

    # change back
    os.chdir('..')

    # step 5: save m_times dictionary into build/m_times.json and copy build/m_times.json onto device :m_times.json
    m_times.save_new_m_times()


if __name__ == "__main__":
    print('starting lh_lib/ deployment\n')
    run()
    print('\nfinished lh_lib/ deployment')
