import sys


RUNNING_MICROPYTHON = sys.implementation.name == 'micropython'


class PLATFORMS:
    ESP32 = 10
    LINUX_GENERIC = 20
    OTHER = 30
    RASPBERRYPI = 40
    WINDOWS = 50


if sys.platform == 'esp32':
    PLATFORM = PLATFORMS.ESP32
elif sys.platform == 'win32':
    PLATFORM = PLATFORMS.WINDOWS
elif sys.platform == 'linux':
    try:
        # alternative: os.uname().nodename.startswith('RasperryPi')  # theres a typo in the implementation: Rasp(b)erry
        with open('/sys/firmware/devicetree/base/model') as f:
            if 'raspberry pi' in f.read().lower():
                PLATFORM = PLATFORMS.RASPBERRYPI
            else:
                PLATFORM = PLATFORMS.LINUX_GENERIC
    except FileNotFoundError:
        PLATFORM = PLATFORMS.LINUX_GENERIC
else:
    PLATFORM = PLATFORMS.OTHER
