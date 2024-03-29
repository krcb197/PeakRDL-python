"""
A hardware simulator to show how the gpio example works
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

    pass