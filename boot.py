"""
This is the MicroPython boot.py for this projects ESP32 chips.
This script gets executed on every startup before main.py.

We will activate WiFi station-connection, but not WebREPl (web cli) as it is not reliable
"""

import network
import time
import machine
# import webrepl


WIFI_DEVICE_NAME = 'ESP32-5'

WIFI_CREDENTIALS = {
}  # ssid: password

WEBREPL_PASSWORD = 'esp32batch'


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(dhcp_hostname=WIFI_DEVICE_NAME)

try:
    while not wlan.isconnected():
        print("Scanning for Wifi:")

        wlan_list = wlan.scan()
        if not wlan_list:
            print("No WLAN found, don't know why.")
            raise KeyboardInterrupt()

        for ssid, bssid, _, _, _, _ in wlan_list:
            ssid = ssid.decode()
            print("Found: {}...".format(ssid))

            if ssid in WIFI_CREDENTIALS:
                print(" credentials provided.")
                print("Connecting...")
                wlan.connect(ssid, WIFI_CREDENTIALS[ssid], bssid=bssid)

                start_time = time.ticks_ms()
                while (not wlan.isconnected()) and (time.ticks_ms() - start_time < 10000):
                    time.sleep_ms(100)

                if wlan.isconnected():
                    print(" SUCCESS")
                    break
                else:
                    print(" FAILED. Trying next one.")
            else:
                print(" no credentials provided.")

        if not wlan.isconnected():
            print("No connectable network found. Retrying in 10 seconds.")
            time.sleep_ms(10000)
except KeyboardInterrupt:
    print("moving on without WLAN\n")
else:
    print("network config: {}\n".format(wlan.ifconfig()))

machine.freq(240000000)
print("adjusted machine frequency to max: 240MHz (default: 160MHz)\n\n")

# webrepl.start(password=WEBREPL_PASSWORD)
# print("webREPL started with password: {}".format(WEBREPL_PASSWORD))
