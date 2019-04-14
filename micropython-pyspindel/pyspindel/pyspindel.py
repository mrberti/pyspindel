"""
This file contains the main routines for the pyspindel.

TODO: Implement everything
"""
try:
    import json
except ImportError:
    import ujson as json

try:
    import socket
except ImportError:
    import usocket as socket

try:
    import time
except ImportError:
    import utime as socket

import gc

# SOCKETS
SOCK_MULTICAST = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# SETTINGS
SETTINGS_FILE_PATH = "pyspindel.conf"
SETTINGS_DEFAULT = {
    "test": 2,
    "tcp_local_bind": "0.0.0.0",
    "tcp_port": 6265,
    "tcp_accept_timeout": 3,
    "tcp_recv_buffer_size": 128,
    "multicast_group": "224.1.1.1",
    "multicast_port": 6265,
}

class PySpindel(object):
    def __init__(self, i2c, reset=False):
        try:
            self._settings = self.read_settings()
        except OSError as exc:
            print("Could not read config file. {}".format(exc))
            reset=True
        if reset:
            print("Resetting to default settings")
            # Default settings
            self._settings = SETTINGS_DEFAULT
            self.save_settings()
        print(self._settings)

        self._i2c = i2c
        self._sock_tcp = None
        self._sock_remote = None
        self.init_socket()

    # SETTINGS RELATED -------------------------------------------------
    def save_settings(self):
        with open(SETTINGS_FILE_PATH, "w+") as settings_file:
            json.dump(self._settings, settings_file)

    def read_settings(self):
        with open(SETTINGS_FILE_PATH, "r") as settings_file:
            return json.load(settings_file)

    def set(self, setting, value):
        if setting not in self._settings:
            print("'{}' not in settings. Creating new setting."
                  .format(setting))
        self._settings[setting] = value

    def get(self, setting):
        if setting in self._settings:
            return self._settings[setting]
        else:
            if setting in SETTINGS_DEFAULT:
                return SETTINGS_DEFAULT[setting]
            else:
                raise IndexError("Could not get setting '{}'".format(setting))

    # SOCKET RELATED ---------------------------------------------------
    def send_multicast(self, message, multicast_group=None, multicast_port=None):
        if not multicast_group:
            multicast_group = self.get("multicast_group")
        if not multicast_port:
            multicast_port = self.get("multicast_port")
        try:
            message_raw = message.encode("utf-8")
        except AttributeError:
            message_raw = str(message).encode("utf-8")
        print("Sending multicast to '{}:{}': {!r}".format(
                multicast_group,
                multicast_port,
                message_raw))
        SOCK_MULTICAST.sendto(
            message_raw,
            (multicast_group, multicast_port))

    def init_socket(self):
        if not self._sock_tcp:
            print("Initializing local socket")
            self._sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            addr = socket.getaddrinfo(
                self.get("tcp_local_bind"),
                self.get("tcp_port"))[0][-1]
            self._sock_tcp.bind(addr)
            self._sock_tcp.listen(1)

    def poll_connection(self, timeout=None):
        if not timeout:
            timeout = self.get("tcp_accept_timeout")
        if not self._sock_tcp:
            self.init_socket()
        self._sock_tcp.settimeout(timeout)
        print("Waiting for TCP connection...")
        try:
            self._sock_remote, addr = self._sock_tcp.accept()
        except OSError:
            print("{} No connection".format(time.time()))
            return False
        print("Got connection from: {}".format(addr))
        return True

    def recv_data(self):
        self._sock_tcp.settimeout(None)
        if self._sock_remote:
            self._sock_remote.settimeout(None)
            data_raw = self._sock_remote.recv(self.get("tcp_recv_buffer_size"))
            if data_raw:
                return data_raw.decode("utf-8")
                return data_raw
            # Connection was closed by the remote
            self._sock_remote.close()
            self._sock_remote = None
        return None

    def close_connection(self):
        if self._sock_remote:
            self._sock_remote.close()
            self._sock_remote = None
        if self._sock_tcp:
            self._sock_tcp.close()
            del self._sock_tcp
            gc.collect()
            self._sock_tcp = None

def main(i2c=None, wifi=None):
    pyspindel = PySpindel(i2c=i2c, reset=True)
    pyspindel.set("muh", 1)
    pyspindel.save_settings()
    print(pyspindel.get("muh"))
    pyspindel.send_multicast(1.2)
    while 1:
        if pyspindel.poll_connection():
            connection_alive = True
            while connection_alive:
                data = pyspindel.recv_data()
                if data:
                    print("Got data: {!r}".format(data))
                else:
                    print("Connection closed")
                    break
            # pyspindel.close_connection()
        # print("rssi = {}".format(wifi.status("rssi")))
        # if not wifi.isconnected():
        #     print("NO WIFI")

if __name__ == "__main__":
    main()


# from .mpu6050 import MPU6050
# def main(i2c):
#     print("Running pyspindel main")
#     import time
#     from math import (sqrt, sin, cos, pi, e, acos)
#     Ts = 100000 # us
#     mpu = MPU6050(i2c)
#     mpu.init()
#     mpu.start()

#     while 1:
#         t_start = time.ticks_us()
#         val = mpu.get_accel()
#         x = val[0]#/16384
#         y = val[1]#/16384
#         z = val[2]#/16384
#         r = sqrt(x*x + y*y + z*z)
#         sign = 1 if (y > 0) else -1
#         phi = sign * acos(z / sqrt(y**2 + z**2))
#         y2 = cos(phi) * y - sin(phi) * z
#         z2 = sin(phi) * y + cos(phi) * z
#         theta = acos(z2 / r)
#         print("{}, {:6.0f},{:6.0f},{:6.0f},{:6.0f},{:6.0f},{:6.0f},{:6.1f},{:6.1f}"
#               .format(
#                 time.ticks_ms(),
#                 x, y, z,
#                 y2, z2, r,
#                 phi * 180 / pi, theta * 180 / pi))
#         # t_diff = time.ticks_diff(time.ticks_us(), t_start)
#         # print("{}".format(t_diff))
#         while time.ticks_diff(time.ticks_us(), t_start) < Ts:
#             time.sleep_us(100)
