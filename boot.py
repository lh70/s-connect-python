"""
This is the MicroPython boot.py for this projects ESP32 chips.
This script gets executed on every startup before main.py.

We will activate WiFi station-connection as well as activate WebREPl (web cli)
"""

import network
import utime
# import webrepl


WIFI_DEVICE_NAME = 'ESP32-2'

WIFI_CREDENTIALS = {
}  # ssid: password

WEBREPL_PASSWORD = 'esp32batch'


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(dhcp_hostname=WIFI_DEVICE_NAME)


while not wlan.isconnected():
    print("Scanning for Wifi:")
    for ssid, bssid, _, _, _, _ in wlan.scan():
        ssid = ssid.decode()
        print("Found: {}...".format(ssid))

        if ssid in WIFI_CREDENTIALS:
            print(" credentials provided.")
            print("Connecting...")
            wlan.connect(ssid, WIFI_CREDENTIALS[ssid], bssid=bssid)

            start_time = utime.ticks_ms()
            while (not wlan.isconnected()) and (utime.ticks_ms() - start_time < 10000):
                utime.sleep_ms(500)

            if wlan.isconnected():
                print(" SUCCESS")
                break
            else:
                print(" FAILED. Trying next one.")
        else:
            print(" no credentials provided.")

    if not wlan.isconnected():
        print("No connectable network found. Retrying.")
        utime.sleep_ms(20000)

print("network config: {}", wlan.ifconfig())

# webrepl.start(password=WEBREPL_PASSWORD)
# print("webREPL started with password: {}".format(WEBREPL_PASSWORD))
