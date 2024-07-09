"""
PeakRDL Python example to show the different methods to access the a register array
"""
from optimised_array_access.reg_model.optimised_array_access import optimised_array_access_cls
from optimised_array_access.sim.optimised_array_access import optimised_array_access_simulator_cls

from optimised_array_access.lib import NormalCallbackSet



if __name__ == '__main__':

    # create an instance of the address map with the simulated callback necessary to demonstrate
    # the example
    sim = optimised_array_access_simulator_cls(0)
    dut = optimised_array_access_cls(callbacks=NormalCallbackSet(read_block_callback=sim.read_block,
                                                                 write_block_callback=sim.write_block,
                                                                 read_callback=sim.read,
                                                                 write_callback=sim.write))

    # the following will involve 2 reads and 2 writes (one per feild) for each register (8 in total)
    for idx in range(len(dut.gpio_register)):
        dut.gpio_register[idx].gpio_direction.write(dut.gpio_register[idx].gpio_direction.enum_cls.GPIO_OUT)
        dut.gpio_register[idx].gpio_pullup.write(False)
        # leave the drive strength untouched

    # the following will involve 1 reads and 1 writes for each register (8 in total)
    # also note the use of the register array iterator (so you don't need range and indexing)
    for gpio_register in dut.gpio_register:
        with gpio_register.single_read_modify_write() as reg:
            reg.gpio_direction.write(reg.gpio_direction.enum_cls.GPIO_OUT)
            reg.gpio_pullup.write(False)
            # leave the drive strength untouched

    # the following will do one block read and one block write for the same thing
    with dut.gpio_register.single_read_modify_write() as reg_array:
        for reg in reg_array:
            reg.gpio_direction.write(reg.gpio_direction.enum_cls.GPIO_OUT)
            reg.gpio_pullup.write(False)
            # leave the drive strength untouched
