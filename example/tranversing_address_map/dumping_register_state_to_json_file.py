import json
from typing import Union

from chip_with_registers.reg_model.chip_with_registers import chip_with_registers_cls
from chip_with_registers.sim.chip_with_registers import chip_with_registers_simulator_cls

from chip_with_registers.lib import NormalCallbackSet, RegReadOnly, RegReadWrite, \
    MemoryReadOnly, MemoryReadWrite, RegFile, AddressMap, RegReadOnlyArray, RegReadWriteArray, \
    AddressMapArray, RegFileArray, MemoryReadOnlyArray, MemoryReadWriteArray


class RegisterDumper:

    def __init__(self, node: AddressMap):
        """
        Class to read all the readable registers in a design and write them to a file

        Args:
            node: AddressMap node to process
        """
        self.address_map = node

    @property
    def registers(self):
        """

        Returns: dictionary with all the register and their field values for the top level node

        """
        return self._process_section(self.address_map)

    def json_dump(self, filename):
        """
        Write all the readable registers out to a JSON file

        Args:
            filename: file to be written to

        Returns: None

        """
        with open(filename, encoding='utf-8', mode='w') as fp:
            json.dump(self.registers, fp, indent=4)

    @staticmethod
    def _process_registers(node: Union[MemoryReadOnly, MemoryReadWrite, RegFile, AddressMap]):
        """
        Process all the registers that are in a memory or section

        Args:
            node: a RegFile, AddressMap or Memory to process

        Returns:
            dictionary with all the register and their field values

        """
        registers_dump = {}
        for register in node.get_readable_registers(unroll=False):

            # the register arrays are put into a list
            if isinstance(register, (RegReadOnlyArray, RegReadWriteArray)):
                array_dump = []
                for register_instance in register:
                    array_dump.append(register_instance.read_fields())
                registers_dump[register.inst_name] = array_dump

            elif isinstance(register, (RegReadOnly, RegReadWrite)):
                registers_dump[register.inst_name] = register.read_fields()

            else:
                raise TypeError('unexpected type encoutered')

        return registers_dump

    def _process_memory(self, node: Union[MemoryReadOnly, MemoryReadWrite]):
        """
        In a memory all the registers must be dumped out

        Args:
            node: Memory Node

        Returns:
            dictionary with all the register and their field values

        """
        return self._process_registers(node)

    def _process_section(self, node: Union[RegFile, AddressMap]):
        """
        In a section all the sub-sections and registers must be dumped out

        Args:
            node: a RegFile or AddressMapto process

        Returns:
            dictionary with all the register and their field values

        """
        registers_dump = {}

        # process all the sections in the section
        for section in node.get_sections(unroll=False):
            if isinstance(section, (RegFileArray, AddressMapArray)):
                array_dump = []
                for section_instance in section:
                    array_dump.append(self._process_section(section_instance))
                registers_dump[section.inst_name] = array_dump

            elif isinstance(section, (RegFile, AddressMap)):
                registers_dump[section.inst_name] = self._process_section(section)
            else:
                raise TypeError('unexpected type encoutered')

        # process all the memories in the section, note only AddressMaps can have memories within
        # them
        if isinstance(node, AddressMap):
            for memory in node.get_memories(unroll=False):
                if isinstance(memory, (MemoryReadOnlyArray, MemoryReadWriteArray)):
                    array_dump = []
                    for memory_instance in memory:
                        array_dump.append(self._process_memory(memory_instance))
                    registers_dump[memory.inst_name] = array_dump

                elif isinstance(memory, (MemoryReadOnly, MemoryReadWrite)):
                    registers_dump[memory.inst_name] = self._process_memory(memory)
                else:
                    raise TypeError('unexpected type encoutered')

        # process all the registers in the section
        registers_dump.update(self._process_registers(node))

        return registers_dump


if __name__ == '__main__':

    # create an instance of the address map with the simulated callback necessary to demonstrate
    # the example
    sim = chip_with_registers_simulator_cls(0)
    dut = chip_with_registers_cls(callbacks=NormalCallbackSet(read_callback=sim.read,
                                                              write_callback=sim.write))

    # generate an instance of the RegisterDumper and write the registers to a file
    reg_dumper = RegisterDumper(dut)
    reg_dumper.json_dump('reg_dump.json')