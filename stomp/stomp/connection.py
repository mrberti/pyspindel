try:
    from .message import STOMPMessage, STOMPMessageError
    from .settings import SETTINGS
except ImportError:
    from message import STOMPMessage, STOMPMessageError
    from settings import SETTINGS


CONN_STATUS_RESET = 0
CONN_STATUS_CONNECTED = 1
CONN_STATUS_DISCONNECTED = 128
CONN_STATUS_CLOSED = 256


MESSAGE_BUFFER_SIZE = 128
RECV_BUFFER_SIZE = SETTINGS.get("tcp_recv_buffer_size")

EOM = SETTINGS.get("eom")

class STOMPConnection(object):
    def __init__(self, socket_remote):
        self._sock_remote = socket_remote
        self._state = CONN_STATUS_RESET
        # self._message_buffer = bytearray(b"\x00") * MESSAGE_BUFFER_SIZE
        self._message_buffer = ""
        self._frames = []

        # client related status
        self._cl_accept_version = ""
        self._cl_host = ""
        self._cl_login = ""
        self._cl_passcode = ""
        self._cl_heart_beat = ""
        self._cl_subscriptions = {}

        # server related status
        self._sv_version = ""
        self._sv_heart_beat = ""
        self._sv_session = ""
        self._sv_server = ""

    def recv(self):
        recv_data = self._sock_remote.recv(RECV_BUFFER_SIZE).decode("utf-8")
        if not recv_data:
            # Received empty string => Connection was closed by the client
            print("Connection closed by client {}.".format(self._sock_remote))
            self.close()
            return False
        print("Received data {!r} from {}".format(recv_data, self._sock_remote))
        if len(recv_data) + len(self._message_buffer) > MESSAGE_BUFFER_SIZE:
            self.error("Message buffer size {} exceeded.".format(MESSAGE_BUFFER_SIZE), "buffer-error")
            return False
        self._message_buffer = self._message_buffer + recv_data
        if EOM in self._message_buffer:
            frame_count = self._message_buffer.count(EOM)
            print("Received {} Frames. Message buffer: {!r}".format(frame_count, self._message_buffer))
            frame_list = self._message_buffer.split(EOM)
            for frame_no in range(frame_count):
                self._frames.append(
                    frame_list[frame_no].lstrip("\r").lstrip("\n") + EOM)
            if frame_count < len(frame_list):
                self._message_buffer = frame_list[-1].lstrip("\r").lstrip("\n")
        return True

    def send(self, stomp_message):
        # TODO
        try: # DANGER TRY!!
            self._sock_remote.send(str(stomp_message).encode("utf-8"))
        except:
            pass
        print(stomp_message)

    def isclosed(self):
        return bool(self._state == CONN_STATUS_CLOSED)

    def handle_frames(self):
        for frame_no in range(len(self._frames)):
            frame = self._frames.pop(0)
            if not self.handle_message(frame):
                return False
        return True

    def handle_message(self, message):
        try:
            stomp_msg = STOMPMessage(message=message)
        except STOMPMessageError as exc:
            self.error(str(exc), "exception")
            return False

        # State machine
        if self._state == CONN_STATUS_RESET:
            if self.accept_connection(stomp_msg):
                self._state == CONN_STATUS_CONNECTED
                return True
        elif self._state == CONN_STATUS_CONNECTED:
            sw_client_handler = {
                # These are all allowed client frames according to STOMP
                # specification
                "SEND": self.cl_send,
                "SUBSCRIBE": self.subscribe,
                "UNSUBSCRIBE": self.unsubscribe,
                "ACK": self.ack,
                "NACK": self.nack,
                "BEGIN": self.begin,
                "COMMIT": self.commit,
                "ABORT": self.abort,
                "DISCONNECT": self.disconnect,
            }
            func = sw_client_handler.get(stomp_msg.command)
            if func:
                return func(stomp_msg)
        elif self._state == CONN_STATUS_DISCONNECTED:
            # Clients SHOULD not send any messages anymore
            return True
        else:
            raise IndexError("Not such a state: {}".format(self._state))
        print("STATE MACHINE FALL THROUGH")
        return False

    def cl_send(self, stomp_msg):
        return True

    def subscribe(self, stomp_msg):
        return True

    def unsubscribe(self, stomp_msg):
        return True

    def ack(self, stomp_msg):
        return True

    def nack(self, stomp_msg):
        return True

    def begin(self, stomp_msg):
        return True

    def commit(self, stomp_msg):
        return True

    def abort(self, stomp_msg):
        return True

    def disconnect(self, stomp_msg):
        # TODO: The sending of the receipt should be defered until all
        # received frames have been handled
        if "receipt" in stomp_msg.header:
            receipt_id = stomp_msg.header["receipt"]
        return self.receipt(receipt_id)

    def receipt(self, id):
        header = {
            "receipt-id": str(id),
        }
        stomp_msg = STOMPMessage("RECEIPT", header)
        self.send(stomp_msg)
        return True

    def accept_connection(self, stomp_message):
        if not (stomp_message.command == "CONNECT"
                or stomp_message.command == "STOMP"):
            self.error("Expected CONNECT message.", "connection-refused")
            return False
        if not ("host" in stomp_message.header):
            self.error("Wrong header.", "connection-refused")
            return False
        if not ("accept-version" in stomp_message.header):
            version = self._cl_accept_version = "1.0"
        else:
            version = stomp_message.header["accept-version"]
        heartbeat = ""
        session = ""
        server = self._sv_server
        header_reply = {
                "version": version,
            }
        if heartbeat: header_reply["heart-beat"] = heartbeat
        if session: header_reply["session"] = session
        if server: header_reply["server"] = server
        stomp_reply = STOMPMessage("CONNECTED", header_reply)
        self.send(stomp_reply)
        return True

    def error(self, error_message, error_message_short="", receipt_id=""):
        """Send an ``ERROR`` Message and close the connection."""
        header = {
                "content-length": len(error_message),
                "content-type": "text/plain",
            }
        if error_message_short:
            header["message"] = error_message_short
        if receipt_id:
            header["receipt-id"] = receipt_id
        stomp_error_msg = STOMPMessage("ERROR",
                                       header,
                                       error_message)
        self.send(stomp_error_msg)
        # According to STOMP specification, the server must close the
        # connection when an ERROR frame was sent.
        # TODO: There should be a certain wait time before closing the
        # socket to make sure the message arrives at the client.
        # Requires asynchronouse sleep.
        self.close()

    def close(self):
        """Close the connection."""
        # TODO
        self._state = CONN_STATUS_CLOSED
        print("STOMP connection closed.")

    def shutdown(self, reason=""):
        print("Connection shutdown. Reason: {}".format(reason))
        self.error(reason, "shutdown")


def main():
    msgs = [
        "CONNECT\n\n^@",
        "CONNEC\n\n^@",
    ]
    con = STOMPConnection(None)
    for msg in msgs:
        con.handle_message(msg)

if __name__ == "__main__":
    main()
