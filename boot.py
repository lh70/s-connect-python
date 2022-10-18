"""
This is the MicroPython boot.py for this projects ESP32 chips.
This script gets executed on every startup before main.py.

We will activate WiFi station-connection, but not WebREPl (web cli) as it is not reliable
"""

import machine
# import webrepl


try:
    from lh_lib.base.network_stack.wlan import connect, ifconfig
    connect()
    print(f'network config: {ifconfig()}\n')
except KeyboardInterrupt:
    print('interrupt by user...moving on without wlan\n')
except ImportError:
    print('lh_lib does not exist...moving on without wlan\n')


machine.freq(240000000)
print('adjusted machine frequency to max: 240MHz (default: 160MHz)\n\n')

# WEBREPL_PASSWORD = 'esp32batch'
# webrepl.start(password=WEBREPL_PASSWORD)
# print("webREPL started with password: {}".format(WEBREPL_PASSWORD))
