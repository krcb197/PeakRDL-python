"""
PeakRDL Python example to show the different methods to access the fields of a register
"""
from optimised_access.reg_model.optimised_access import optimised_access_cls
from optimised_access.sim.optimised_access import optimised_access_simulator_cls

from optimised_access.lib import NormalCallbackSet


if __name__ == '__main__':

    # create an instance of the address map with the simulated callback necessary to demonstrate
    # the example
    sim = optimised_access_simulator_cls(0)
    dut = optimised_access_cls(callbacks=NormalCallbackSet(read_callback=sim.read,
                                                           write_callback=sim.write))

    # configure the GPIO 0 and GPIO 1 without affecting the state of the GPIO 2 and GPIO 3
    # configuration.

    # the direction field enumeration is needed to, it is found field attribute, note that the
    # same enumeration definition can be used for all channels in this case
    direction_enum = dut.gpio_register.gpio_0_dir.enum_cls

    # This can be done either using the ``write_fields`` method
    dut.gpio_register.write_fields(gpio_0_dir=direction_enum.GPIO_OUT,
                                   gpio_0_pullup=False,
                                   gpio_0_strength=2,
                                   gpio_1_dir=direction_enum.GPIO_IN)

    # It can also be done with the context manager
    with dut.gpio_register.single_read_modify_write() as reg:
        reg.gpio_0_dir.write(direction_enum.GPIO_OUT)
        reg.gpio_0_pullup.write(False)
        reg.gpio_0_strength.write(2)
        reg.gpio_0_dir.write(direction_enum.GPIO_IN)