"""
This script deploys changes to lh_lib onto a microcontroller connected to the same network.
There must be at least the base module, as well as wlan.json, boot.py and main.py deployed on the device.
The framework must be running on the device.

This script must (currently) be run on the host device.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import time
import json
import binascii

try:
    from lh_lib.base.network_stack.client import Client
except ImportError:
    sys.path.insert(1, os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    from lh_lib.base.network_stack.client import Client

from lh_lib.base.serializable_data_types import ControlMessageFilesystem, ControlMessageReboot

DEVICE_ADDRESS = '192.168.2.124'
DEVICE_PORT = 8090

DEPLOY_STARTUP_FILES = False  # if set, copies boot.py, main.py and wlan.json onto the device (!!! make sure there is a hostname set in wlan.json and that there is at least one pair of valid credentials set (ssid -> pw) !!!)
DEPLOY_BASE_ONLY = True  # if set, deploys only the base module with the base_worker

PRE_COMPILE = True  # Pre-compiles files to .mpy format
NATIVE_CODE = False  # True currently not usable. Uses to much RAM on device. Alternative: use the @micropython.native function decorator
MPY_MARCH = 'xtensawin'  # ESP32

if sys.implementation.name == 'micropython':
    raise Exception("Call this script on a host platform with your microcontroller connected! (python remote-deployment.py)")


"""
Utility Classes
"""


class Flags:

    def __init__(self, device):
        self.device = device

        result = self.device.read_file('/flags.json')
        if result['type'] == 'error':
            print("could not retrieve flags.json. creating new one.")
            self.old_flags = {}
        else:
            print("using existing flags.json for reference.")
            self.old_flags = json.loads(result['data'].decode('utf8'))  # i know there is actually a utf8 encoded json string in this file

    def flags_match(self):
        try:
            return self.old_flags['PRE_COMPILE'] == PRE_COMPILE and self.old_flags['NATIVE_CODE'] == NATIVE_CODE and self.old_flags['MPY_MARCH'] == MPY_MARCH
        except KeyError:
            return False

    def save_to_device(self):
        print('saving new flags to device :flags.json')
        result = self.device.write_string_to_file(json.dumps({'PRE_COMPILE': PRE_COMPILE, 'NATIVE_CODE': NATIVE_CODE, 'MPY_MARCH': MPY_MARCH}), '/flags.json')
        if result['type'] == 'error':
            raise Exception('failed on writing flags to device, return was: {}'.format(result))


class MTimes:

    def __init__(self, device=None):
        self.struct = {}
        self.device = device

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
        result = self.device.read_file('/m_times.json')
        if result['type'] == 'error':
            print("could not retrieve device m_times.json. creating new one.")
        else:
            print("using existing m_times.json for reference.")
            self.struct = json.loads(result['data'].decode('utf8'))  # i know there is actually a utf8 encoded json string in this file

    def save_to_device(self):
        print('saving new build m_times to device :m_times.json')
        result = self.device.write_string_to_file(json.dumps(self.struct['build']), '/m_times.json')
        if result['type'] == 'error':
            raise Exception('failed on writing m_times to device, return was: {}'.format(result))


class DeviceRemoteFilesystemAccess:

    def __init__(self, host, port):
        self.client = Client(host, port)

    def path_stat(self, path):
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_STAT, path).serializable())
        return self.client.recv_wait()

    def read_file(self, filepath):
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_READ_FILE, filepath).serializable())
        result = self.client.recv_wait()
        if result['type'] == 'result':
            result['data'] = binascii.a2b_base64(result['data'])
        return result

    def write_file_to_file(self, host_filepath, device_filepath):
        with open(host_filepath, mode='rb') as f:
            escaped_content = binascii.b2a_base64(f.read()).decode('utf8')
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_WRITE_FILE, device_filepath, escaped_content, int(os.stat(host_filepath).st_mtime)).serializable())
        return self.client.recv_wait()

    def write_string_to_file(self, strng, device_filepath):
        escaped_content = binascii.b2a_base64(strng.encode('utf8')).decode('utf8')
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_WRITE_FILE, device_filepath, escaped_content, int(time.time())).serializable())
        return self.client.recv_wait()

    def remove_file(self, filepath):
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_REMOVE_FILE, filepath).serializable())
        return self.client.recv_wait()

    def list_directory(self, dir_path):
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_LIST_DIRECTORY, dir_path).serializable())
        return self.client.recv_wait()

    def remove_directory(self, dir_path):
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_REMOVE_DIRECTORY, dir_path).serializable())
        return self.client.recv_wait()

    def make_directory(self, dir_path):
        self.client.send(ControlMessageFilesystem(ControlMessageFilesystem.COMMAND_MAKE_DIRECTORY, dir_path).serializable())
        return self.client.recv_wait()

    def reboot(self):
        self.client.send(ControlMessageReboot().serializable())
        self.client.recv_acknowledgement()


if __name__ == '__main__':
    # set working directory to repository root for the case that the script is not called from project root
    os.chdir(os.path.dirname(os.path.realpath(os.path.dirname(__file__))))
    print('changed working directory to: {}'.format(os.getcwd()))

    # check if device is reachable
    print('checking device access by opening remote connection...', end='', flush=True)
    device = DeviceRemoteFilesystemAccess(DEVICE_ADDRESS, DEVICE_PORT)
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
                    print('compiling file {} to {}'.format(lib_fp, out_fp))
                    subprocess.run(['mpy-cross', '-o', out_fp, '-march={}'.format(MPY_MARCH), '-X', 'emit={}'.format("native" if NATIVE_CODE else "bytecode"), lib_fp], stderr=subprocess.PIPE, stdout=subprocess.PIPE, check=True)
                else:
                    print('copying file {} to {}'.format(lib_fp, out_fp))
                    shutil.copy2(lib_fp, out_fp)

                build_mtimes.add(out_fp, int(os.stat(lib_fp).st_mtime))  # using int cast, because esp32 float precision cannot handle this long float

    # get device_m_times
    device_mtimes = MTimes(device)
    device_mtimes.load_from_device()

    # get device flags
    device_flags = Flags(device)

    # removing old files
    RESERVED_FILES = ['m_times.json', 'flags.json', 'main.py', 'boot.py', 'wlan.json']
    RESERVED_FILES += ['/' + f for f in RESERVED_FILES[:]]

    for parts in device_mtimes.as_list():
        if not build_mtimes.contains(['build'] + parts):
            fp = '/'.join(parts)

            if fp in RESERVED_FILES:
                continue  # these reserved files may not be deleted, even though they are not in lh_lib

            print('removing ghost file {}'.format(fp))
            result = device.remove_file(fp)
            if result['type'] == 'error':
                print('ghost file {} does not exist on filesystem. ignoring.'.format(fp))

            dir_parts = parts[:-1]
            while len(dir_parts) > 0:
                directory = '/'.join(dir_parts)

                result = device.list_directory(directory)
                if result['type'] == 'error' or result['data']:
                    # non existent directory
                    # or non empty directory
                    break

                # empty directory
                print('removing ghost directory {}'.format(directory))
                result = device.remove_directory(directory)
                if result['type'] == 'error':
                    raise Exception('ghost directory {} could not be removed, return was: {}'.format(directory, result))
                dir_parts = parts[:-1]

    # create directories if they do not exist
    unique_directories = []
    for parts in build_mtimes.as_list():
        directory = '/'.join(parts[1:-1])  # first part is 'build' and last part is "filename"
        if directory not in unique_directories:
            unique_directories.append(directory)

    for directory in unique_directories:
        parts = directory.split('/')
        partial_directory = ''

        while len(parts) > 0:
            partial_directory += '/' + parts.pop(0)

            result = device.path_stat(partial_directory)
            if result['type'] == 'error':
                print('creating non existent directory {} on device'.format(partial_directory))
                result = device.make_directory(partial_directory)
                if result['type'] == 'error':
                    raise Exception('could not create directory {}, return was {}'.format(partial_directory, result))

    # deploy modified and new files
    for parts in build_mtimes.as_list():
        src_fp = '/'.join(parts)
        dst_fp = '/'.join(parts[1:])
        if not device_flags.flags_match() or build_mtimes.get_m_time(parts) > device_mtimes.get_m_time(parts[1:]):
            print('copying host file {} to device :{}'.format(src_fp, dst_fp))
            result = device.write_file_to_file(src_fp, dst_fp)
            if result['type'] == 'error':
                raise Exception('failed on writing {} to device, return was: {}'.format(src_fp, result))

    device_flags.save_to_device()

    if DEPLOY_STARTUP_FILES:
        print('copying additional files of first deployment:')
        print('copying host file wlan.json to device :wlan.json')
        result = device.write_file_to_file('wlan.json', '/wlan.json')
        if result['type'] == 'error':
            raise Exception('failed on writing wlan.json to device, return was: {}'.format(result))
        print('copying host file boot.py to device :boot.py')
        result = device.write_file_to_file('boot.py', '/boot.py')
        if result['type'] == 'error':
            raise Exception('failed on writing boot.json to device, return was: {}'.format(result))
        print('copying host file main.py to device :main.py')
        result = device.write_file_to_file('main.py', '/main.py')
        if result['type'] == 'error':
            raise Exception('failed on writing main.json to device, return was: {}'.format(result))

    print('rebooting device')
    device.reboot()
