"""
An example to turn on GPIO 0 with the RAL, with using peakrdl-python
"""
from gpio.reg_model.gpio import gpio_cls as GPIO
from gpio.sim.gpio import gpio_simulator_cls as HardwareSimulator

from gpio.lib import NormalCallbackSet

if __name__ == '__main__':

    # create an instance of the RAL with the callbacks directed at the hardware simulator
    hw = HardwareSimulator(0)
    gpio = GPIO(callbacks=NormalCallbackSet(read_callback=hw.read, write_callback=hw.write))

    # the direction field enumeration is needed to, it is found field attribute, note that the
    # same enumeration definition can be used for all channels in this case
    direction_enum = gpio.dir.gpio_0_dir.enum_cls

    # Configure GPIO[0] as out
    gpio.dir.gpio_0_dir.write(direction_enum.GPIO_OUT)
    # Configure GPIO[0] state as 1
    gpio.data_out.gpio_0_out.write(1)
