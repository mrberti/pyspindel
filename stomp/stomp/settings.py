try:
    import ujson as json
except ImportError:
    import json


# SETTINGS
EOL = "\r\n"
EOM = "^@" # "\x00"
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
    "eol": EOL,
    "eom": EOM,
}


class STOMPSettings(object):
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

SETTINGS = STOMPSettings(reset=True)
