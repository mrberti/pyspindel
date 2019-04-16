EOL = "\n"
# EOL = "\r\n"
EOM = "^@" # "\x00"

ACCEPTED_COMMANDS = ["CONNECT", "CONNECTED"]

class STOMPMessageError(Exception):
    pass

class STOMPMessage(object):
    def __init__(self, command="", header={}, body="", message=""):
        self.command = command
        self.header = header
        self.body = body
        if message:
            self.parse(message)

    def __str__(self):
        command_str = self.command
        header_str = ""
        for header in self.header.keys():
            header_str += "{}:{}{}".format(header, self.header[header], EOL)
        body_str = self.body
        if body_str:
            msg_str_list = [command_str, header_str, body_str]
        else:
            msg_str_list = [command_str, header_str, ""]
        return "{}{EOM}".format(EOL.join(msg_str_list), EOM=EOM)

    def __repr__(self):
        return repr(str(self))

    def parse(self, message):
        string_list = message.split("\n")
        if len(string_list) < 3:
            raise STOMPMessageError("Not enough lines")
        command = string_list.pop(0).strip("\r")
        if command not in ACCEPTED_COMMANDS:
            raise STOMPMessageError("{!r} not a valid command".format(command))
        header = {}
        for index in range(len(string_list) - 1):
            line = string_list.pop(0).strip("\r")
            if not line:
                body = "\n".join(string_list).strip("\n").strip("\r")
                break
            else:
                try:
                    key, value = line.split(":")
                    header[key] = value
                except ValueError as exc:
                    raise STOMPMessageError("Could not parse header line: "
                                            "{!r}. {}".format(line, exc))
        else:
            raise STOMPMessageError("Message did not contain an empty line.")
        if not body.endswith(EOM):
            raise STOMPMessageError("Body does not contain a valid EOM "
                                    "terminator. {!r}".format(body))
        body = body[0:-len(EOM)]
        self.__init__(command=command, header=header, body=body)

def main():
    msg = STOMPMessage(
        "CONNECT",
        {
            "accept-version": "1.0,1.1,1.2",
            "host": "pyspindel",
        },
        "asdasd")
    # print(repr(msg))
    # print(msg)
    test_msgs = [
        "CONNECT\n\n{EOM}".format(EOM=EOM),
        "CONNECT\n\n{EOM}\r\n".format(EOM=EOM),
        "CONNECT\n\nasd\ntest\n{EOM}\r\n".format(EOM=EOM),
        "CONNECT\nkey:val\n\n{EOM}".format(EOM=EOM),
        "CONNECT\nkey:val\n{EOM}".format(EOM=EOM),
        "CONNECT\n{EOM}".format(EOM=EOM),
        "CONNECT\n\n".format(EOM=EOM),
    ]
    for msg in test_msgs:
        try:
            print(repr(msg), end="")
            msg_parsed = STOMPMessage(message=str(msg))
            print(" => OK")
        except STOMPMessageError as exc:
            print(" => EXCEPTION: {}".format(exc))

if __name__ == "__main__":
    main()
