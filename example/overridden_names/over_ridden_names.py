import json
from typing import Union

from over_ridden_names.reg_model.over_ridden_names import over_ridden_names_cls
from over_ridden_names.lib import NormalCallbackSet

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

if __name__ == '__main__':

    # create an instance of the class
    over_ridden_names = over_ridden_names_cls(callbacks=NormalCallbackSet(read_callback=read_addr_space))

    # access the field value directly
    print(over_ridden_names.overridden_reg_a.overridden_field_a.read())

    # access the feild value using the original systemRDL names
    print(over_ridden_names.get_child_by_system_rdl_name('reg_a').get_child_by_system_rdl_name('field_a').read())