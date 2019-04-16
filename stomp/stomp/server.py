try:
    import ujson as json
except ImportError:
    import json

try:
    import usocket as socket
except ImportError:
    import socket

try:
    import uselect as select
except ImportError:
    import select

try:
    import utime as time
except ImportError:
    import time

import gc


# SOCKETS
SOCK_MULTICAST = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# SETTINGS
EOL = "\r\n"
SETTINGS_FILE_PATH = "stomp.conf"
SETTINGS_DEFAULT = {
    "test": 2,
    "tcp_local_bind": "0.0.0.0",
    "tcp_port": 6265,
    "tcp_accept_timeout": 3,
    "tcp_recv_buffer_size": 128,
    "tcp_new_unaccepted_connections": 5,
    "multicast_group": "224.1.1.1",
    "multicast_port": 6265,
}


class STOMPServer(object):
    def __init__(self, reset=False):
        if not reset:
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

        self._sock = None
        self._sock_remote = None
        self._inputs = []

    # SETTINGS RELATED -------------------------------------------------
    def save_settings(self):
        with open(SETTINGS_FILE_PATH, "w+") as settings_file:
            # json.dump(self._settings, settings_file)
            settings_file.write(json.dumps(self._settings))

    def read_settings(self):
        with open(SETTINGS_FILE_PATH, "r") as settings_file:
            # return json.load(settings_file)
            return json.loads(settings_file.read())

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

    def listen(self):
        print("start listening")
        for sock in self._inputs:
            sock.close()
        del self._sock
        gc.collect()
        print("Initializing local socket")
        addr = socket.getaddrinfo(
            self.get("tcp_local_bind"),
            self.get("tcp_port"))[0][-1]
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(True)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(addr)
        # self._sock.listen(self.get("tcp_new_unaccepted_connections"))
        # ATTENTION: When on Micropython 1.10 and ESP8266 ``backlog``
        # must be >= 2! 
        # See: https://github.com/micropython/micropython/issues/4511
        self._sock.listen(5)
        self._inputs = [self._sock]

    def poll_connection(self, timeout=None):
        if not timeout:
            timeout = self.get("tcp_accept_timeout")
        if not self._sock:
            self.listen()
        self._sock.settimeout(timeout)
        print("Waiting for TCP connection...")
        try:
            self._sock_remote, addr = self._sock.accept()
        except OSError:
            print("{} No connection".format(time.time()))
            return False
        print("Got connection from: {}".format(addr))
        return True

    def handle_connections(self, timeout=1):
        if not self._sock:
            raise Exception("Tried to access a None Socket.")
        readables, writeables, exceptionals = select.select(
            self._inputs, [], self._inputs, timeout)
        for readable in readables:
            if readable is self._sock:
                # The server is able to accept a remote connection
                print("Accepting new connection...")
                remote, addr = readable.accept()
                remote.setblocking(True)
                self._inputs.append(remote)
                print("Client connection established: {}"
                    .format(addr))
            else:
                # The client has sent data
                # TODO: USING id(socket) TO KEEP TRACK!!!
                recv_data = readable.recv(self.get("tcp_recv_buffer_size"))
                print("Received data {!r} from {}".format(recv_data, readable))
                if not recv_data:
                    # Received empty string => Connection closed by client
                    self._inputs.remove(readable)
                    readable.close()
                    print("Connection closed by client {}.".format(readable))
                else:
                    # Received ordinary data. Parse lines and put into the
                    # receive queue.
                    pass

        for writable in writeables:
            print("writable: {}".format(writable))

        for exceptional in exceptionals:
            print("exceptional: {}".format(exceptional))
            exceptional.close()
            self._inputs.remove(exceptional)

    def recv_data(self):
        self._sock.settimeout(None)
        if self._sock_remote:
            self._sock_remote.settimeout(None)
            data_raw = self._sock_remote.recv(self.get("tcp_recv_buffer_size"))
            print(repr(data_raw))
            if data_raw:
                return data_raw.decode("utf-8")
            # Connection was closed by the remote
            self._sock_remote.close()
            self._sock_remote = None
        return None

    def close_connection(self):
        if self._sock_remote:
            self._sock_remote.close()
            self._sock_remote = None
        if self._sock:
            self._sock.close()
            del self._sock
            gc.collect()
            self._sock = None

def main():
    stomp_server = STOMPServer()
    # stomp_server.set("muh", 1)
    # stomp_server.save_settings()
    # print(stomp_server.get("muh"))
    # stomp_server.send_multicast(time.time())
    stomp_server.listen()
    time.sleep(1)
    while 1:
        # try:
        stomp_server.handle_connections()
        # except Exception as exc:
            # print("{}".format(exc))
        # if stomp_server.poll_connection():
        #     connection_alive = True
        #     while connection_alive:
        #         data = stomp_server.recv_data()
        #         if data:
        #             print("Got data: {!r}".format(data))
        #         else:
        #             print("Connection closed")
        #             break
            # stomp_server.close_connection()
        # print("rssi = {}".format(wifi.status("rssi")))
        # if not wifi.isconnected():
        #     print("NO WIFI")

if __name__ == "__main__":
    main()
