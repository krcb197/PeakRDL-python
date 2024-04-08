"""
An example to turn on GPIO 0 with just read and write
"""

class HardwareSimulator:
    def __init__(self):
        # use a python dictionary to simulate the hardware
        self._address_space = {0x100: 0, 0x104: 0}

    def read(self, addr: int, width: int = 32, accesswidth: int = 32) -> int:
        """
        function to simulate a device read
        """
        return self._address_space[addr]


    def write(self, addr: int, data: int, width: int=32, accesswidth: int=32) -> None:
        """
        function to simulate a device read
        """
        self._address_space[addr] = data

if __name__ == '__main__':

    # make an instance of the hardware simulator
    hw = HardwareSimulator()

    # 1. Read the DIR register (to make sure you preserve the states of other pins)
    dir_reg = hw.read(0x100)
    # 2. Take the read value of the DIR register, force bit 0 to `1` then write it back
    hw.write(0x100, dir_reg | (1 << 0)) # force bit 0 with bitwise OR
    # 3. Read the DATA_OUT register (to make sure you preserve the states of other pins)
    data_out_reg = hw.read(0x104)
    # 4. Take the read value of the DATA_OUT register, force bit 0 to `1` then write it back
    hw.write(0x104, data_out_reg | (1 << 0))  # force bit 0 with bitwise OR