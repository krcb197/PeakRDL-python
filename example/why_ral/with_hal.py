"""
An example to turn on GPIO 0 with a Hardware Abstaction Layer, built on top of the peakrdl-python
Register Abstraction Layer (RAL)
"""
from enum import Enum, auto
from gpio.reg_model.gpio import gpio_cls as GPIO
from gpio.sim.gpio import gpio_simulator_cls as HardwareSimulator

class GPIODir(Enum):
    """
    Enumeration for GPIO direction
    """
    IN = auto()
    OUT = auto()

from gpio.lib import NormalCallbackSet

class HAL:

    class GPIO_HAL:
        def __init__(self, ral: GPIO, channel:int):
            self._chn = channel
            self._ral = ral

        @property
        def __direction_field(self):
            return getattr(self._ral.dir, f'gpio_{self._chn}_dir')

        @property
        def __data_out_field(self):
            return getattr(self._ral.data_out, f'gpio_{self._chn}_out')

        @property
        def __gpio_enum(self):
            return self.__direction_field.enum_cls

        @property
        def direction(self) -> GPIODir:
            ral_enum_value = self.__direction_field.read()
            if ral_enum_value is self.__gpio_enum.GPIO_IN:
                return GPIODir.IN
            if ral_enum_value is self.__gpio_enum.GPIO_OUT:
                return GPIODir.OUT
            raise ValueError(f'Unable to map {ral_enum_value}')

        @direction.setter
        def direction(self, dir: GPIODir):
            mappping_dict = {
                GPIODir.IN: self.__gpio_enum.GPIO_IN,
                GPIODir.OUT: self.__gpio_enum.GPIO_OUT,
            }
            self.__direction_field.write(mappping_dict[dir])

        @property
        def data_out(self) -> bool:
            return self.__data_out_field.read()

        @data_out.setter
        def data_out(self, dir: bool):
            if self.direction is not GPIODir.OUT:
                self.direction = GPIODir.OUT
            self.__data_out_field.write(dir)


    def __init__(self, callbacks:NormalCallbackSet):
        self.ral = GPIO(callbacks=callbacks)
        self._gpio = [self.GPIO_HAL(self.ral, chn) for chn in range(8)]

    def __getitem__(self, item):
        return self._gpio[item]

if __name__ == '__main__':

    # create an instance of the HAL with the callbacks directed at the hardware simulator
    hw = HardwareSimulator(0)
    gpio = HAL(callbacks=NormalCallbackSet(read_callback=hw.read, write_callback=hw.write))

    # attempting to set the data_out automatically checks the direction is configured and
    # sets it if necessary
    gpio[0].data_out = True


