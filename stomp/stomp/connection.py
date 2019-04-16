try:
    from .message import STOMPMessage, STOMPMessageError
except ImportError:
    from message import STOMPMessage, STOMPMessageError


CONN_STATUS_RESET = 0


class STOMPConnection(object):
    def __init__(self, socket_local, socket_remote):
        self._sock_local = socket_local # Probably not necessary
        self._sock_remote = socket_remote
        self._state = CONN_STATUS_RESET

    def handle_message(self, message):
        # TODO
        try:
            stomp_msg = STOMPMessage(message=message)
        except STOMPMessageError as exc:
            self.error(str(exc), "exception")
            return
        if self._state == CONN_STATUS_RESET:
            self.accept_connection(stomp_msg)
        else:
            raise IndexError("Not such a state: {}".format(self._state))

    def accept_connection(self, stomp_message):
        if stomp_message.command == "CONNECT":
            stomp_reply = STOMPMessage("CONNECTED", {
                "header": "value",
            })
            self.send(stomp_reply)
        else:
            self.error("Something went wrong...")

    def send(self, stomp_message):
        # TODO
        print(stomp_message)

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
        # TODO: There should be a certain wait time before closing the
        # socket to make sure the message arrives at the client.
        # Requires asynchronouse sleep.
        self.close()

    def close(self):
        """Close the connection."""
        # TODO
        print("Connection closed...")


def main():
    msgs = [
        "CONNECT\n\n^@",
        "CONNEC\n\n^@",
    ]
    con = STOMPConnection(None, None)
    for msg in msgs:
        con.handle_message(msg)

if __name__ == "__main__":
    main()
