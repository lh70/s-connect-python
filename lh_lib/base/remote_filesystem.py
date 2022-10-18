"""
Remote Filesystem Handler

exposes a minimal file manipulating API
"""
import os
import json

from lh_lib.base.serializable_data_types import ControlMessageResponseResult, ControlMessageResponseError
from lh_lib.base.constants import RUNNING_MICROPYTHON


class RemoteFilesystemHandler:

    def __init__(self):
        if RUNNING_MICROPYTHON:
            # must be available through the first direct deployment via usb
            # mtimes are only specially tracked on esp32, because it does not (yet) has access to an accurate time, therefore mtimes is not set on files automatically
            with open('/m_times.json', 'rt') as f:
                self.mtimes = json.load(f)

    def handle_control_message(self, message_content):
        filesystem_command = message_content['command']
        filesystem_path = message_content['path']

        if '\\' in filesystem_path:
            raise Exception('windows style paths (\\) are not allowed')

        try:
            if filesystem_command == 'write_file':
                file_content = message_content['content']
                file_new_mtime = message_content['mtime']
                with open(filesystem_path, 'wt') as f:
                    f.write(file_content)
                if RUNNING_MICROPYTHON:
                    self.add_mtime(filesystem_path, file_new_mtime)
                    with open('/m_times.json', 'wt') as f:
                        json.dump(self.mtimes, f)
                return ControlMessageResponseResult(True)
            elif filesystem_command == 'read_file':
                with open(filesystem_path, 'rt') as f:
                    content = f.read()
                return ControlMessageResponseResult(content)
            elif filesystem_command == 'remove_file':
                os.remove(filesystem_path)
                if RUNNING_MICROPYTHON:
                    self.remove_mtime(filesystem_path)
                    with open('/m_times.json', 'wt') as f:
                        json.dump(self.mtimes, f)
                return ControlMessageResponseResult(True)
            elif filesystem_command == 'path_stat':
                return ControlMessageResponseResult({
                    'stat': os.stat(filesystem_path),
                    'mtime': self.get_mtime(filesystem_path) if RUNNING_MICROPYTHON else None
                })
            elif filesystem_command == 'list_directory':
                return ControlMessageResponseResult(os.listdir(filesystem_path))
            elif filesystem_command == 'make_directory':
                os.mkdir(filesystem_path)
                return ControlMessageResponseResult(True)
            elif filesystem_command == 'remove_directory':
                os.rmdir(filesystem_path)
                return ControlMessageResponseResult(True)
            else:
                raise Exception('invalid filesystem command')
        except (OSError, Exception) as e:
            return ControlMessageResponseError(e)

    def add_mtime(self, fp, m_time):
        parts = fp.split('/')
        sec = self.mtimes
        for part in parts[:-1]:
            if part not in sec:
                sec[part] = {}
            sec = sec[part]
        sec[parts[-1]] = m_time

    def get_mtime(self, fp):
        parts = fp.split('/')
        try:
            sec = self.mtimes
            for part in parts:
                sec = sec[part]
        except KeyError:
            return 0
        return sec

    def remove_mtime(self, fp):
        def recursive_remove(remaining_parts, remaining_mtimes):
            try:
                if len(remaining_parts) == 1:
                    if not isinstance(remaining_mtimes[remaining_parts[0]], dict):
                        del remaining_mtimes[remaining_parts[0]]
                    else:
                        raise Exception('path to remove mtime from is no file')
                else:
                    recursive_remove(remaining_parts[1:], remaining_mtimes[remaining_parts[0]])
                    if not remaining_mtimes[remaining_parts[0]]:
                        del remaining_mtimes[remaining_parts[0]]
            except KeyError:
                raise Exception('filepath to remove mtime from is not in mtimes')

        recursive_remove(fp.split('/'), self.mtimes)

