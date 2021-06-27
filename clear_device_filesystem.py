import os
import sys

RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'

if not RUNNING_MICROPYTHON:
    raise Exception("Call this script on the microcontroller directly! (mpremote run clear_device_filesystem.py)")


def gather_files_and_directories(root=''):
    files = []
    directories = []
    # iterate over all files and directories in root. node-tuple size is system dependend: name, type, inode, (size)
    for node in os.ilistdir(root):
        name = node[0]
        node_type = node[1]

        fp = '{}/{}'.format(root, name)

        # boot script is not removed
        # would have no consequences, but our wifi config is gone with a bare boot.py on next reboot
        if fp == '/boot.py':
            continue

        if node_type == 0x4000:
            # recursively gather files from directories
            print('found directory: {}'.format(fp))
            directories.append(fp)
            files += gather_files_and_directories(fp)
        elif node_type == 0x8000:
            # add files
            print('found file: {}'.format(fp))
            files.append(fp)
        else:
            raise Exception('{} has unknown filesystem type {}'.format(fp, node_type))

    return files, directories


file_paths, dir_paths = gather_files_and_directories()

for p in file_paths:
    print('removing file: {}'.format(p))
    os.remove(p)

for p in dir_paths:
    print('removing directory: {}'.format(p))
    os.remove(p)
