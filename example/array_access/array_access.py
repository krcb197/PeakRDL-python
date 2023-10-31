import json
from typing import Union

from array_access.reg_model.array_access import array_access_cls
from array_access.lib.callbacks import NormalCallbackSet

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
    over_ridden_names = array_access_cls(callbacks=NormalCallbackSet(read_callback=read_addr_space))

    # access a entry in the 1D array
    print(over_ridden_names.reg_array_1D[0].field_a.read())

    # loop over all the elements in the 1D array, without the index being exposed
    for array_item in over_ridden_names.reg_array_1D:
        print(array_item.field_a.read())

    # loop over all the elements in the 1D array, with the index being exposed
    for index, array_item in over_ridden_names.reg_array_1D.items():
        print(f'item[{index[0]}]={array_item.field_a.read():d}')

    # access a entry in the 3D array
    print(over_ridden_names.reg_array_3D[1][1][1].field_a.read())

    # access a entry in the 3D array with other indexing scheme
    print(over_ridden_names.reg_array_3D[1,1,1].field_a.read())

    # loop over all the elements in the 3D array, without the index being exposed
    for array_item in over_ridden_names.reg_array_3D:
        print(array_item.field_a.read())

    # loop over all the elements in the 1D array, with the index being exposed
    for index, array_item in over_ridden_names.reg_array_3D.items():
        # convert the index which is a tuple of integers to a comma delimited string
        index_str = ','.join([str(index_element) for index_element in index])
        print(f'item[{index_str}]={array_item.field_a.read():d}')

    # perform an operation to one axis of the array
    for array_item in over_ridden_names.reg_array_3D[0,0,0::]:
        print(array_item.field_a.read())