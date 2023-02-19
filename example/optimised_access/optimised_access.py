"""
PeakRDL Python example to show the different methods to access the fields of a register
"""
from optimised_access.reg_model.optimised_access import optimised_access_cls, \
    optimised_access_gpio_direction_enc_enumcls

from optimised_access.lib import NormalCallbackSet

# dummy functions to demonstrate the class
def read_addr_space(addr: int, width: int, accesswidth: int) -> int:
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
    return int(0)


def write_addr_space(addr: int, width: int, accesswidth: int, data: int) -> None:
    """
    Callback to simulate the operation of the package, everytime the read is called, it will
    request the user input the value to be read back.

    Args:
        addr: Address to write to
        width: Width of the register in bits
        accesswidth: Minimum access width of the register in bits
        data: value to be written to the register

    Returns:
        None
    """
    print(f'0x{data:X} written to 0x{addr:X}')

if __name__ == '__main__':

    # create an instance of the address map with the simulated callback necessary to demonstrate
    # the example
    dut = optimised_access_cls(callbacks=NormalCallbackSet(read_callback=read_addr_space,
                                                           write_callback=write_addr_space))

    # configure the GPIO 0 and GPIO 1 without affecting the state of the GPIO 2 and GPIO 3
    # configuration.

    # This can be done either using the ``write_fields`` method
    dut.gpio_register.write_fields(gpio_0_dir=optimised_access_gpio_direction_enc_enumcls.GPIO_OUT,
                                   gpio_0_pullup=False,
                                   gpio_0_strength=2,
                                   gpio_1_dir=optimised_access_gpio_direction_enc_enumcls.GPIO_IN)

    # It can also be done with the context manager
    with dut.gpio_register.single_read_modify_write() as reg:
        reg.gpio_0_dir.write(optimised_access_gpio_direction_enc_enumcls.GPIO_OUT)
        reg.gpio_0_pullup.write(False)
        reg.gpio_0_strength.write(2)
        reg.gpio_0_dir.write(optimised_access_gpio_direction_enc_enumcls.GPIO_IN)