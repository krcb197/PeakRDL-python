import json
from typing import Union

from chip_with_registers.reg_model.chip_with_registers import chip_with_registers_cls
from chip_with_registers.sim.chip_with_registers import chip_with_registers_simulator_cls

from chip_with_registers.lib import NormalCallbackSet,  RegWriteOnly, RegReadWrite, \
    MemoryWriteOnly, MemoryReadWrite, RegFile, AddressMap


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
                raise TypeError('unexpected type encountered')

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
                raise TypeError('unexpected type encountered')

        # process all the memories in the section, note only AddressMaps can have memories within
        # them
        if isinstance(node, AddressMap):
            for memory in node.get_memories(unroll=True):
                if isinstance(memory, (MemoryWriteOnly, MemoryReadWrite)):
                    self._process_memory(memory)
                else:
                    raise TypeError('unexpected type encountered')

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
    sim = chip_with_registers_simulator_cls(0)
    dut = chip_with_registers_cls_with_reset(callbacks=NormalCallbackSet(read_callback=sim.read,
                                                                         write_callback=sim.write))

    dut.reset()
