"""
An example to turn on GPIO 0 with the RAL
"""
from gpio.reg_model.gpio import gpio_cls as GPIO
from gpio.sim.gpio import gpio_simulator_cls as HardwareSimulator
from gpio.reg_model.gpio import gpio_gpio_direction_enc_enumcls as GPIO_DIR_ENUM

from gpio.lib import NormalCallbackSet

if __name__ == '__main__':

    # create an instance of the RAL with the callbacks directed at the hardware simulator
    hw = HardwareSimulator(0)
    gpio = GPIO(callbacks=NormalCallbackSet(read_callback=hw.read, write_callback=hw.write))

    # Configure GPIO[0] as out
    gpio.dir.gpio_0_dir.write(GPIO_DIR_ENUM.GPIO_OUT)
    # Configure GPIO[0] state as 1
    gpio.data_out.gpio_0_out.write(1)
