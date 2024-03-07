"""
PeakRDL Python example to show the different methods to access the a register array
"""
from array import array as Array

from optimised_array_access.reg_model.optimised_array_access import optimised_array_access_cls

from optimised_array_access.lib import NormalCallbackSet

# dummy functions to demonstrate the class
def read_block(addr: int, width: int, accesswidth: int, length: int) -> Array:
    """
    Callback to simulate the operation of the package, everytime the read block is called
    returns an arroy of zeros

    Args:
        addr: Address to write to
        width: Width of the register in bits
        accesswidth: Minimum access width of the register in bits

    Returns:
        value inputted by the used
    """
    return Array('L', [0 for _ in range(length)])

def read(addr: int, width: int, accesswidth: int) -> int:
    """
    Callback to simulate the operation of the package, everytime the read is called, it return
    an integer value of 0

    Args:
        addr: Address to write to
        width: Width of the register in bits
        accesswidth: Minimum access width of the register in bits

    Returns:
        value inputted by the used
    """
    return 0

def write_block(addr: int, width: int, accesswidth: int, data: int) -> None:
    """
    Callback to simulate the operation of the package, everytime the write block is called it
    will print out the contents

    Args:
        addr: Address to write to
        width: Width of the register in bits
        accesswidth: Minimum access width of the register in bits
        data: value to be written to the register

    Returns:
        None
    """
    value_str = ','.join([f'0x{value:X}' for value in data])
    print(f'data written to address 0x{addr:X} = {value_str}')

def write(addr: int, width: int, accesswidth: int, data: int) -> None:
    """
    Callback to simulate the operation of the package, everytime the write is called it
    will print out the contents

    Args:
        addr: Address to write to
        width: Width of the register in bits
        accesswidth: Minimum access width of the register in bits
        data: value to be written to the register

    Returns:
        None
    """
    print(f'data written to address 0x{addr:X} = 0x{data:X}')

if __name__ == '__main__':

    # create an instance of the address map with the simulated callback necessary to demonstrate
    # the example
    dut = optimised_array_access_cls(callbacks=NormalCallbackSet(read_block_callback=read_block,
                                                                 write_block_callback=write_block,
                                                                 read_callback=read,
                                                                 write_callback=write))

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
