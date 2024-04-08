"""
A demonstration of using enumeration
"""
from enumerated_fields.lib import NormalCallbackSet

from enumerated_fields.reg_model.enumerated_fields import enumerated_fields_cls as GPIO
from enumerated_fields.sim.enumerated_fields import enumerated_fields_simulator_cls as HardwareSimulator

if __name__ == '__main__':

    # create an instance of the hardware simulator
    hw = HardwareSimulator(0)
    # create an instance of the RAL with the callbacks directed at the hardware simulator
    gpio = GPIO(callbacks=NormalCallbackSet(read_callback=hw.read, write_callback=hw.write))

    # get the field values
    for field in gpio.gpio_strength.readable_fields:
        print(f'{field.inst_name} has strength {field.read().name} [0x{field.read().value}]')

    # set the field values by retrieving the enum class from the class itself
    CurrentEnum = gpio.gpio_strength.gpio_0.enum_cls
    gpio.gpio_strength.gpio_0.write(CurrentEnum.STRENGTH_12MA)