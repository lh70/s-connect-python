"""
This is the MicroPython boot.py for this projects ESP32 chips.
This script gets executed on every startup before main.py.

We will activate WiFi station-connection as well as activate WebREPl (web cli)
"""

import network
import utime
# import webrepl

import lh_lib.logging

from lh_lib.logging import log


WIFI_DEVICE_NAME = 'ESP32-1'

WIFI_CREDENTIALS = {
}  # ssid: password

WEBREPL_PASSWORD = 'esp32batch'


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(dhcp_hostname=WIFI_DEVICE_NAME)

'''
Set this to True for testing purposes if you run it manually
'''
log_state = lh_lib.logging.ACTIVE
lh_lib.logging.ACTIVE = False

while not wlan.isconnected():
    log("Scanning for Wifi:")
    for ssid, bssid, _, _, _, _ in wlan.scan():
        ssid = ssid.decode()
        log("Found: {}...".format(ssid))

        if ssid in WIFI_CREDENTIALS:
            log(" credentials provided.")
            log("Connecting...")
            wlan.connect(ssid, WIFI_CREDENTIALS[ssid], bssid=bssid)

            start_time = utime.ticks_ms()
            while (not wlan.isconnected()) and (utime.ticks_ms() - start_time < 10000):
                utime.sleep_ms(500)

            if wlan.isconnected():
                log(" SUCCESS")
                break
            else:
                log(" FAILED. Trying next one.")
        else:
            log(" no credentials provided.")

    if not wlan.isconnected():
        log("No connectable network found. Retrying.")
        utime.sleep_ms(20000)

log("network config: {}", wlan.ifconfig())

# webrepl.start(password=WEBREPL_PASSWORD)
# print("webREPL started with password: {}".format(WEBREPL_PASSWORD))

'''
Preserve originally intended logging active state
'''
lh_lib.logging.ACTIVE = log_state
