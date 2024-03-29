"""
A demonstration of using enumeration
"""
from enumerated_fields.lib import NormalCallbackSet

from enumerated_fields.reg_model.enumerated_fields import enumerated_fields_cls as GPIO

class HardwareSimulator:
    def __init__(self):
        # use a python dictionary to simulate the hardware
        self._address_space = {0x00: 0, 0x04: 0}

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

    # create an instance of the hardware simulator
    hw = HardwareSimulator()
    # create an instance of the RAL with the callbacks directed at the hardware simulator
    gpio = GPIO(callbacks=NormalCallbackSet(read_callback=hw.read, write_callback=hw.write))

    # get the field values
    for field in gpio.gpio_strength.readable_fields:
        print(f'{field.inst_name} has strength {field.read().name} [0x{field.read().value}]')

    # set the field values by retrieving the enum class from the class itself
    CurrentEnum = gpio.gpio_strength.gpio_0.enum_cls
    gpio.gpio_strength.gpio_0.write(CurrentEnum.STRENGTH_12MA)