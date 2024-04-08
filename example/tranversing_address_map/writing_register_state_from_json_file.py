import json
from typing import Union, Dict, List

from chip_with_registers.reg_model.chip_with_registers import chip_with_registers_cls
from chip_with_registers.sim.chip_with_registers import chip_with_registers_simulator_cls

from chip_with_registers.lib import NormalCallbackSet, RegWriteOnly, RegReadWrite, \
    MemoryWriteOnly, MemoryReadWrite, RegFile, AddressMap, RegWriteOnlyArray, RegReadWriteArray, \
    AddressMapArray, RegFileArray, MemoryWriteOnlyArray, MemoryReadWriteArray, FieldEnum, Field


class RegisterWriter:

    def __init__(self, node: AddressMap):
        """
        Class to read all the readable registers in a design and write them to a file

        Args:
            node: AddressMap node to process
        """
        self.address_map = node

    @property
    def register_template(self):
        """
        Returns: dictionary with all the writable registers, with the values set to None
        """
        return self._section_template(self.address_map)

    def json_template_generate(self, filename):
        """
        Write out a Template JSON file, with all the filed values set to None

        Args:
            filename: file to be written to

        Returns: None
        """
        with open(filename, encoding='utf-8', mode='w') as fp:
            json.dump(self.register_template, fp, indent=4)

    def configure_registers_from_json(self, filename):
        """
        Read JSON file, which matchs the structure of the registers and set any register field with
        a non-null value

        Args:
            filename: file to be read in

        Returns: None
        """
        with open(filename, encoding='utf-8', mode='r') as fp:
            reg_from_json = json.load(fp)

        self._process_json_leaf(node=self.address_map, reg_from_json=reg_from_json)

    @staticmethod
    def _registers_template(node: Union[MemoryWriteOnly, MemoryReadWrite, RegFile, AddressMap]):
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
            if isinstance(register, (RegWriteOnlyArray, RegReadWriteArray)):
                array_dump = []
                for register_instance in register:
                    field_set = {}
                    for field in register_instance.writable_fields:
                        field_set[field.inst_name] = None
                    array_dump.append(field_set)
                    field_set['inst_name'] = register_instance.inst_name
                registers_dump[register.inst_name] = array_dump

            elif isinstance(register, (RegWriteOnly, RegReadWrite)):
                field_set = {}
                for field in register.writable_fields:
                    field_set[field.inst_name] = None
                field_set['inst_name'] = register.inst_name
                registers_dump[register.inst_name] = field_set
            else:
                raise TypeError('unexpected type encoutered')

        return registers_dump

    def _memory_template(self, node: Union[MemoryWriteOnly, MemoryReadWrite]):
        """
        In a memory all the registers templated

        Args:
            node: Memory Node

        Returns:
            dictionary with all the register and their field values

        """
        registers_in_memory = self._registers_template(node)
        registers_in_memory['inst_name'] = node.inst_name
        return registers_in_memory

    def _section_template(self, node: Union[RegFile, AddressMap]):
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
                    array_dump.append(self._section_template(section_instance))
                registers_dump[section.inst_name] = array_dump

            elif isinstance(section, (RegFile, AddressMap)):
                registers_dump[section.inst_name] = self._section_template(section)
            else:
                raise TypeError('unexpected type encoutered')

        # process all the memories in the section, note only AddressMaps can have memories within
        # them
        if isinstance(node, AddressMap):
            for memory in node.get_memories(unroll=False):
                if isinstance(memory, (MemoryWriteOnlyArray, MemoryReadWriteArray)):
                    array_dump = []
                    for memory_instance in memory:
                        array_dump.append(self._memory_template(memory_instance))
                    registers_dump[memory.inst_name] = array_dump

                elif isinstance(memory, (MemoryWriteOnly, MemoryReadWrite)):
                    registers_dump[memory.inst_name] = self._memory_template(memory)
                else:
                    raise TypeError('unexpected type encountered')

        # process all the registers in the section
        registers_dump.update(self._registers_template(node))
        registers_dump['inst_name'] = node.inst_name

        return registers_dump

    def _process_json_leaf(self, node: Union[RegFile, AddressMap, MemoryWriteOnly, MemoryReadWrite], reg_from_json: Dict[str, Union[Dict, List]]):
        """
        In a section all the sub-sections and registers written

        Args:
            node: a RegFile or AddressMap to process
            reg_from_json: a dictionary (or sub-section of it) that came from a JSON file

        Returns:
            None
        """
        if 'inst_name' in reg_from_json:
            inst_name_from_dict = reg_from_json.pop('inst_name')
            if inst_name_from_dict != node.inst_name:
                raise ValueError(f'inst_name from json leaf does not match node')
        else:
            raise KeyError('inst_name is missing from json leaf')

        for key, value in reg_from_json.items():
            if hasattr(node, key):
                child_node = getattr(node, key)
                if isinstance(value, list):
                    # if the leaf is a list, then the child node should be an array of one type
                    # or another
                    if not isinstance(child_node, (AddressMapArray, RegFileArray,
                                                   MemoryWriteOnlyArray, MemoryReadWriteArray,
                                                   RegWriteOnlyArray, RegReadWriteArray)):
                        raise AttributeError(f'node was a list but the match value was not an array')
                    if len(value) != len(child_node):
                        raise ValueError('child node array and json leaf list do not match in length')
                    # make a match iterator between all the elements in the leaf list and the
                    # array of nodes
                    for value_entry, child_node_indexed in zip(value, child_node):
                        self._process_json_leaf(node=child_node_indexed, reg_from_json=value_entry)
                elif isinstance(child_node, (AddressMap, RegFile,
                                             MemoryReadWrite, MemoryWriteOnly,
                                             RegWriteOnly, RegReadWrite)):
                    self._process_json_leaf(node=child_node, reg_from_json=value)
                elif isinstance(child_node,(Field, FieldEnum)):
                    if value is None:
                        continue

                    # if the field is an enumerated field, the field_value from the json file
                    # must be converted
                    if isinstance(child_node, FieldEnum):
                        child_node.write(child_node.enum_cls(value))
                    else:
                        child_node.write(value)
                else:
                    raise TypeError(f'Unhandled child node type:{type(child_node)}')

            else:
                raise AttributeError(f'entry:{key} not present in node:{node}')




if __name__ == '__main__':

    # create an instance of the address map with the simulated callback necessary to demonstrate
    # the example
    sim = chip_with_registers_simulator_cls(0)
    dut = chip_with_registers_cls(callbacks=NormalCallbackSet(read_callback=sim.read,
                                                              write_callback=sim.write))

    # generate an instance of the RegisterWriter and write the template JSON file for registers
    # in the design. In the template all the values are set to null (None in python)
    reg_writer = RegisterWriter(dut)
    reg_writer.json_template_generate('reg_template.json')

    # reading the file and set one value, this process would normally be done by hand. However,
    # for the sake of this
    with open('reg_template.json', encoding='utf-8', mode='r') as fp:
        reg_dict = json.load(fp)

    reg_dict['regfile_array'][0]['reg_array'][1]['first_field'] = 1
    reg_dict['regfile_array'][1]['reg_array'][0]['second_field'] = 1

    with open('reg_to_write.json', encoding='utf-8', mode='w') as fp:
        json.dump(reg_dict, fp, indent=4)

    # set all the registers with a non-null value from the JSON file, when this example is run we
    # expect to see a single register write occur
    reg_writer.configure_registers_from_json('reg_to_write.json')
