"""
Copies files we need on the device from /submodules to /lh_lib/included_submodules_files

This script is just to keep track of the used submodule files and their origin.

Manually to /lh_lib/included_submodules_files added files:
ssd1306.py  | from https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py
"""

import os
import pathlib
import shutil


# ( from filepath | to directory )
# based on repository root
FILES_TO_COPY = (
    ('submodules/python_lcd/lcd/esp32_gpio_lcd.py', 'lh_lib/included_submodules_files'),
    ('submodules/python_lcd/lcd/lcd_api.py',        'lh_lib/included_submodules_files')
)


def run():
    # set working directory to repository root for the case that the script is not called in its directory
    path_to_repo_root = pathlib.Path(__file__).parent.parent.resolve(strict=True)
    os.chdir(path_to_repo_root)

    for source_path, destination_path in FILES_TO_COPY:
        shutil.copy2(
            pathlib.Path(source_path).resolve(strict=True),
            pathlib.Path(destination_path).resolve(strict=True))


if __name__ == '__main__':
    run()
