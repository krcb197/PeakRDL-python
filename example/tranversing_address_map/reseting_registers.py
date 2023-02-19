import json
from typing import Union

from chip_with_registers.reg_model.chip_with_registers import chip_with_registers_cls

from chip_with_registers.lib import NormalCallbackSet,  RegWriteOnly, RegReadWrite, \
    MemoryWriteOnly, MemoryReadWrite, RegFile, AddressMap


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


class chip_with_registers_cls_with_reset(chip_with_registers_cls):
    """
    Extends the chip_with_registers_cls class adding methods to reset all the registers to
    there defined reset values
    """

    @staticmethod
    def _process_registers(node: Union[MemoryWriteOnly, MemoryReadWrite, RegFile, AddressMap]):
        """
        Process all the registers that are in a memory or section

        Args:
            node: a RegFile, AddressMap or Memory to process

        Returns:
            dictionary with all the register and their field values

        """

        for register in node.get_writable_registers(unroll=True):

            if isinstance(register, (RegWriteOnly, RegReadWrite)):
                reset_value_dict = {}
                for field in register.writable_fields:
                    reset_value = field.default
                    if reset_value is not None:
                        reset_value_dict[field.inst_name] = reset_value
                if len(reset_value_dict) > 0:
                    register.write_fields(**reset_value_dict)
            else:
                raise TypeError('unexpected type encoutered')

    def _process_memory(self, node: Union[MemoryWriteOnly, MemoryReadWrite]):
        """
        In a memory all the registers must be dumped out

        Args:
            node: Memory Node

        Returns:
            None

        """
        self._process_registers(node)

    def _process_section(self, node: Union[RegFile, AddressMap]):
        """
        In a section all the sub-sections and registers must be dumped out

        Args:
            node: a RegFile or AddressMapto process

        Returns:
            None

        """

        # process all the sections in the section
        for section in node.get_sections(unroll=True):
            if isinstance(section, (RegFile, AddressMap)):
                self._process_section(section)
            else:
                raise TypeError('unexpected type encoutered')

        # process all the memories in the section, note only AddressMaps can have memories within
        # them
        if isinstance(node, AddressMap):
            for memory in node.get_memories(unroll=True):
                if isinstance(memory, (MemoryWriteOnly, MemoryReadWrite)):
                    self._process_memory(memory)
                else:
                    raise TypeError('unexpected type encoutered')

        # process all the registers in the section
        self._process_registers(node)

    def reset(self):
        """
        Resets all the registers in the address map to their default values

        Returns:
            None

        """
        self._process_section(self)

if __name__ == '__main__':

    # create an instance of the address map with the simulated callback necessary to demonstrate
    # the example
    dut = chip_with_registers_cls_with_reset(
        callbacks=NormalCallbackSet(read_callback=read_addr_space,
                                    write_callback=write_addr_space))

    dut.reset()