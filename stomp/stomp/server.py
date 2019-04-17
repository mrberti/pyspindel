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

try:
    from .connection import STOMPConnection
    from .settings import SETTINGS
except ImportError:
    from connection import STOMPConnection
    from settings import SETTINGS


# SOCKETS
SOCK_MULTICAST = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class STOMPServer(object):
    def __init__(self):
        self._sock = None
        self._inputs = []
        self._connections = {}

    # SOCKET RELATED ---------------------------------------------------
    def send_multicast(self, message, multicast_group=None, multicast_port=None):
        if not multicast_group:
            multicast_group = SETTINGS.get("multicast_group")
        if not multicast_port:
            multicast_port = SETTINGS.get("multicast_port")
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
        print("Initializing local socket")
        addr = socket.getaddrinfo(
            SETTINGS.get("tcp_local_bind"),
            SETTINGS.get("tcp_port"))[0][-1]
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(True)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(addr)
        # ATTENTION: When on Micropython 1.10 and ESP8266 ``backlog``
        # must be >= 2!
        # See: https://github.com/micropython/micropython/issues/4511
        print("Start listening")
        # self._sock.listen(5)
        self._sock.listen(SETTINGS.get("tcp_new_unaccepted_connections"))
        self._inputs = [self._sock]

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
                stomp_connection = STOMPConnection(remote)
                self._connections[id(remote)] = stomp_connection
                print("Client connection established: {}"
                    .format(addr))
            else:
                # The client has sent data
                stomp_connection = self._connections[id(readable)]
                stomp_connection.recv()
                stomp_connection.handle_frames()
                if stomp_connection.isclosed():
                    self._inputs.remove(readable)
                    readable.close()
                    del self._connections[id(readable)]

        for writable in writeables:
            print("writable: {}".format(writable))

        for exceptional in exceptionals:
            print("exceptional: {}".format(exceptional))
            exceptional.close()
            self._inputs.remove(exceptional)

    def shutdown(self, reason=""):
        print("Shutting down server. Active connections: {}"
              .format(len(self._connections)))
        for key in self._connections.keys():
            self._connections[key].shutdown(reason)
        self._inputs = []
        self._connections = {}
        gc.collect()

def main():
    stomp_server = STOMPServer()
    stomp_server.listen()
    time.sleep(1)
    try:
        while 1:
            stomp_server.handle_connections()
    except KeyboardInterrupt:
        pass
    stomp_server.shutdown("The server was shutdown by a KeyboardInterrupt")

if __name__ == "__main__":
    main()
