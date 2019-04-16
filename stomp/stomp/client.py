try:
    from .message import STOMPMessage
except ImportError:
    from message import STOMPMessage


class STOMPClient(object):
    def __init__(self):
        pass


def main():
    msg = STOMPMessage(
    "CONNECT",
    {
        "accept-version": "1.0,1.1,1.2",
        "host": "pyspindel",
    },
    "")
    print(msg)


if __name__ == "__main__":
    main()
