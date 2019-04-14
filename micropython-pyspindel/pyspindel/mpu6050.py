try:
    import struct
except ImportError:
    import ustruct as struct

MPU6050_ADDR_BASE = 104

class MPU6050Error(Exception):
    pass

class MPU6050(object):
    def __init__(self, i2c, baudrate=400000, a0=0):
        self.i2c = i2c
        self.baudrate = baudrate
        self.buf_accel = bytearray(6)
        self.buf_gyro = bytearray(6)
        self.buf_temp = bytearray(1)
        self.off_a_x = 5200
        self.off_a_y = 0
        self.off_a_z = -1816
        self.off_g_x = 0
        self.off_g_y = 0
        self.off_g_z = 0
        self._address = MPU6050_ADDR_BASE + a0

    def init(self):
        pass

    def is_connected(self):
        return bool(self._address in self.i2c.scan())

    def start(self):
        if not self.is_connected():
            raise MPU6050Error("MPU6050 is not connected on I2C bus.")
        self.i2c.writeto_mem(self._address, 107, b"\x00")

    def stop(self):
        pass

    def get_accel(self):
        self.i2c.readfrom_mem_into(self._address, 59, self.buf_accel)
        accel = struct.unpack(">hhh", self.buf_accel)
        a_x = (accel[0] - self.off_a_x) # / 16384
        a_y = (accel[0] - self.off_a_y) # / 16384
        a_z = (accel[0] - self.off_a_z) # / 16384
        return (a_x, a_y, a_z)

    def get_gyro(self):
        self.i2c.readfrom_mem_into(self._address, 67, self.buf_gyro)
        gyro = struct.unpack(">hhh", self.buf_gyro)
        return gyro

    def get_temp(self):
        self.i2c.readfrom_mem_into(self._address, 65, self.buf_temp)
        temp = struct.unpack(">h", self.buf_temp)[0] / 340 + 36.53
        return temp


def main():
    pass


if __name__ == "__main__":
    main()
