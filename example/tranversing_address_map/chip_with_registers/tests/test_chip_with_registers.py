"""
Unit Tests for the chip_with_registers register model Python Wrapper

This code was generated from the PeakRDL-python package
"""
from array import array as Array
import unittest
from unittest.mock import patch, call
import random
from itertools import combinations
import math

from ..lib import CallbackSet

from ..reg_model.chip_with_registers import chip_with_registers_cls

# dummy functions to support the test cases, note that these are not used as
# they get patched
def read_addr_space(addr: int, width: int, accesswidth: int):
    assert isinstance(addr, int)
    assert isinstance(width, int)
    assert isinstance(accesswidth, int)
    return 0

def write_addr_space(addr: int, width: int, accesswidth: int,  data: int):
    assert isinstance(addr, int)
    assert isinstance(width, int)
    assert isinstance(accesswidth, int)
    assert isinstance(data, int)

def read_callback(addr: int, width: int, accesswidth: int):
    return read_addr_space(addr=addr, width=width, accesswidth=accesswidth)

def read_block_addr_space(addr: int, width: int, accesswidth: int, length:int) -> Array:
    assert isinstance(addr, int)
    assert isinstance(width, int)
    assert isinstance(accesswidth, int)
    assert isinstance(length, int)

    if width == 32:
        typecode = 'L'
    elif width == 64:
        typecode = 'Q'
    elif width == 16:
        typecode = 'I'
    elif width == 8:
        typecode = 'B'
    else:
        raise ValueError('unhandled memory width')

    return Array(typecode, [0 for x in range(length)])

def read_block_callback(addr: int, width: int, accesswidth: int, length: int):
    return read_block_addr_space(addr=addr, width=width, accesswidth=accesswidth, length=length)

def write_callback(addr: int, width: int, accesswidth: int,  data: int):
    write_addr_space(addr=addr, width=width, accesswidth=accesswidth, data=data)

def write_block_addr_space(addr: int, width: int, accesswidth: int,  data: Array):
    assert isinstance(addr, int)
    assert isinstance(width, int)
    assert isinstance(accesswidth, int)
    assert isinstance(data, Array)

def write_block_callback(addr: int, width: int, accesswidth: int,  data: Array):
    write_block_addr_space(addr=addr, width=width, accesswidth=accesswidth, data=data)

class chip_with_registers_TestCase(unittest.TestCase):

    def setUp(self):
        self.dut = chip_with_registers_cls(CallbackSet(read_callback=read_callback,
                                                          write_callback=write_callback))

    @staticmethod
    def _reverse_bits(value: int, number_bits: int) -> int:
        """

        Args:
            value: value to reverse
            number_bits: number of bits used in the value

        Returns:
            reversed valued
        """
        result = 0
        for i in range(number_bits):
            if (value >> i) & 1:
                result |= 1 << (number_bits - 1 - i)
        return result

    def test_inst_name(self):
        """
        Walk the address map and check the inst name has been correctly populated
        """
        self.assertEqual(self.dut.regfile_array[0].inst_name, 'regfile_array[0]')
        self.assertEqual(self.dut.regfile_array[0].full_inst_name, 'chip_with_registers.regfile_array[0]')
        self.assertEqual(self.dut.regfile_array[0].single_reg.inst_name, 'single_reg')
        self.assertEqual(self.dut.regfile_array[0].single_reg.full_inst_name, 'chip_with_registers.regfile_array[0].single_reg')
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.full_inst_name, 'chip_with_registers.regfile_array[0].single_reg.first_field')
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.full_inst_name, 'chip_with_registers.regfile_array[0].single_reg.second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].inst_name, 'reg_array[0]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[0]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[0].first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[0].second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].inst_name, 'reg_array[1]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[1]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[1].first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[1].second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].inst_name, 'reg_array[2]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[2]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[2].first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[2].second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].inst_name, 'reg_array[3]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[3]')
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[3].first_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.full_inst_name, 'chip_with_registers.regfile_array[0].reg_array[3].second_field')
        self.assertEqual(self.dut.regfile_array[1].inst_name, 'regfile_array[1]')
        self.assertEqual(self.dut.regfile_array[1].full_inst_name, 'chip_with_registers.regfile_array[1]')
        self.assertEqual(self.dut.regfile_array[1].single_reg.inst_name, 'single_reg')
        self.assertEqual(self.dut.regfile_array[1].single_reg.full_inst_name, 'chip_with_registers.regfile_array[1].single_reg')
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.full_inst_name, 'chip_with_registers.regfile_array[1].single_reg.first_field')
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.full_inst_name, 'chip_with_registers.regfile_array[1].single_reg.second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].inst_name, 'reg_array[0]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[0]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[0].first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[0].second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].inst_name, 'reg_array[1]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[1]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[1].first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[1].second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].inst_name, 'reg_array[2]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[2]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[2].first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[2].second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].inst_name, 'reg_array[3]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[3]')
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[3].first_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.full_inst_name, 'chip_with_registers.regfile_array[1].reg_array[3].second_field')
        self.assertEqual(self.dut.single_regfile.inst_name, 'single_regfile')
        self.assertEqual(self.dut.single_regfile.full_inst_name, 'chip_with_registers.single_regfile')
        self.assertEqual(self.dut.single_regfile.single_reg.inst_name, 'single_reg')
        self.assertEqual(self.dut.single_regfile.single_reg.full_inst_name, 'chip_with_registers.single_regfile.single_reg')
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.full_inst_name, 'chip_with_registers.single_regfile.single_reg.first_field')
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.full_inst_name, 'chip_with_registers.single_regfile.single_reg.second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[0].inst_name, 'reg_array[0]')
        self.assertEqual(self.dut.single_regfile.reg_array[0].full_inst_name, 'chip_with_registers.single_regfile.reg_array[0]')
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[0].first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[0].second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[1].inst_name, 'reg_array[1]')
        self.assertEqual(self.dut.single_regfile.reg_array[1].full_inst_name, 'chip_with_registers.single_regfile.reg_array[1]')
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[1].first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[1].second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[2].inst_name, 'reg_array[2]')
        self.assertEqual(self.dut.single_regfile.reg_array[2].full_inst_name, 'chip_with_registers.single_regfile.reg_array[2]')
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[2].first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[2].second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[3].inst_name, 'reg_array[3]')
        self.assertEqual(self.dut.single_regfile.reg_array[3].full_inst_name, 'chip_with_registers.single_regfile.reg_array[3]')
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.inst_name, 'first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[3].first_field')
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.inst_name, 'second_field')
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.full_inst_name, 'chip_with_registers.single_regfile.reg_array[3].second_field')
        

    def test_register_properties(self):
        """
        Walk the address map and check the address, size and accesswidth of every register is
        correct
        """
        self.assertEqual(self.dut.regfile_array[0].single_reg.address, 0)
        self.assertEqual(self.dut.regfile_array[0].single_reg.width, 32)
        self.assertEqual(self.dut.regfile_array[0].single_reg.accesswidth, self.dut.regfile_array[0].single_reg.accesswidth)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].address, 4)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].width, 32)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].accesswidth, self.dut.regfile_array[0].reg_array[0].accesswidth)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].address, 8)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].width, 32)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].accesswidth, self.dut.regfile_array[0].reg_array[1].accesswidth)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].address, 12)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].width, 32)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].accesswidth, self.dut.regfile_array[0].reg_array[2].accesswidth)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].address, 16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].width, 32)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].accesswidth, self.dut.regfile_array[0].reg_array[3].accesswidth)
        self.assertEqual(self.dut.regfile_array[1].single_reg.address, 20)
        self.assertEqual(self.dut.regfile_array[1].single_reg.width, 32)
        self.assertEqual(self.dut.regfile_array[1].single_reg.accesswidth, self.dut.regfile_array[1].single_reg.accesswidth)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].address, 24)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].width, 32)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].accesswidth, self.dut.regfile_array[1].reg_array[0].accesswidth)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].address, 28)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].width, 32)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].accesswidth, self.dut.regfile_array[1].reg_array[1].accesswidth)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].address, 32)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].width, 32)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].accesswidth, self.dut.regfile_array[1].reg_array[2].accesswidth)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].address, 36)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].width, 32)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].accesswidth, self.dut.regfile_array[1].reg_array[3].accesswidth)
        self.assertEqual(self.dut.single_regfile.single_reg.address, 64)
        self.assertEqual(self.dut.single_regfile.single_reg.width, 32)
        self.assertEqual(self.dut.single_regfile.single_reg.accesswidth, self.dut.single_regfile.single_reg.accesswidth)
        self.assertEqual(self.dut.single_regfile.reg_array[0].address, 68)
        self.assertEqual(self.dut.single_regfile.reg_array[0].width, 32)
        self.assertEqual(self.dut.single_regfile.reg_array[0].accesswidth, self.dut.single_regfile.reg_array[0].accesswidth)
        self.assertEqual(self.dut.single_regfile.reg_array[1].address, 72)
        self.assertEqual(self.dut.single_regfile.reg_array[1].width, 32)
        self.assertEqual(self.dut.single_regfile.reg_array[1].accesswidth, self.dut.single_regfile.reg_array[1].accesswidth)
        self.assertEqual(self.dut.single_regfile.reg_array[2].address, 76)
        self.assertEqual(self.dut.single_regfile.reg_array[2].width, 32)
        self.assertEqual(self.dut.single_regfile.reg_array[2].accesswidth, self.dut.single_regfile.reg_array[2].accesswidth)
        self.assertEqual(self.dut.single_regfile.reg_array[3].address, 80)
        self.assertEqual(self.dut.single_regfile.reg_array[3].width, 32)
        self.assertEqual(self.dut.single_regfile.reg_array[3].accesswidth, self.dut.single_regfile.reg_array[3].accesswidth)

    def test_memory_properties(self):
        """
        Walk the address map and check the address, size and accesswidth of every memory is
        correct
        """

    def test_field_properties(self):
        """
        walk the address map and check:
        - that the lsb and msb of every field is correct
        - that where default values are provided they are applied correctly
        """
        # test field properties: chip_with_registers.regfile_array[0].single_reg.first_field
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].single_reg.second_field
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[0].first_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[0].second_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[1].first_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[1].second_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[2].first_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[2].second_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[3].first_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[0].reg_array[3].second_field
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].single_reg.first_field
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].single_reg.second_field
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[0].first_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[0].second_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[1].first_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[1].second_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[2].first_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[2].second_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[3].first_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.lsb,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.msb,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.low,
                        0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.high,
                         15)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.regfile_array[1].reg_array[3].second_field
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.lsb,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.msb,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.low,
                        16)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.high,
                         17)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.default,
                         0)
        self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.single_reg.first_field
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.lsb,
                        0)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.msb,
                         15)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.low,
                        0)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.high,
                         15)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.single_reg.first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.single_reg.second_field
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.lsb,
                        16)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.msb,
                         17)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.low,
                        16)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.high,
                         17)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.single_reg.second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[0].first_field
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.lsb,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.msb,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.low,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.high,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[0].second_field
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.lsb,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.msb,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.low,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.high,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[1].first_field
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.lsb,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.msb,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.low,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.high,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[1].second_field
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.lsb,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.msb,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.low,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.high,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[2].first_field
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.lsb,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.msb,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.low,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.high,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[2].second_field
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.lsb,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.msb,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.low,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.high,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[3].first_field
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.lsb,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.msb,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.low,
                        0)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.high,
                         15)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.bitmask,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.inverse_bitmask,
                         0xFFFF0000)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.max_value,
                         0xFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.is_volatile,
                         False)
        # test field properties: chip_with_registers.single_regfile.reg_array[3].second_field
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.lsb,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.msb,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.low,
                        16)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.high,
                         17)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.bitmask,
                         0x30000)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.inverse_bitmask,
                         0xFFFCFFFF)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.max_value,
                         0x3)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.default,
                         0)
        self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.is_volatile,
                         False)

    def test_register_read_and_write(self):
        """
        Walk the register map and check every register can be read and written to correctly
        """

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[0].single_reg
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[0].single_reg.read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[0].single_reg.read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[0].single_reg.read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[0].single_reg.read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[0].single_reg.write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[0].single_reg.write(0)
            write_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[0].single_reg.write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].single_reg.write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].single_reg.write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[0].reg_array[0]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[0].reg_array[0].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[0].reg_array[0].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[0].reg_array[0].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[0].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[0].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[0].reg_array[1]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[0].reg_array[1].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[0].reg_array[1].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[0].reg_array[1].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[1].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[1].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[0].reg_array[2]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[0].reg_array[2].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[0].reg_array[2].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[0].reg_array[2].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[2].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[2].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[0].reg_array[3]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[0].reg_array[3].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[0].reg_array[3].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[0].reg_array[3].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[3].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[3].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[1].single_reg
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[1].single_reg.read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[1].single_reg.read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[1].single_reg.read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[1].single_reg.read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[1].single_reg.write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[1].single_reg.write(0)
            write_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[1].single_reg.write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].single_reg.write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].single_reg.write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[1].reg_array[0]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[1].reg_array[0].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[1].reg_array[0].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[1].reg_array[0].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[0].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[0].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[1].reg_array[1]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[1].reg_array[1].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[1].reg_array[1].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[1].reg_array[1].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[1].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[1].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[1].reg_array[2]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[1].reg_array[2].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[1].reg_array[2].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[1].reg_array[2].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[2].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[2].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.regfile_array[1].reg_array[3]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.regfile_array[1].reg_array[3].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.regfile_array[1].reg_array[3].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.regfile_array[1].reg_array[3].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[3].write(-1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[3].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.single_regfile.single_reg
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.single_regfile.single_reg.read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.single_regfile.single_reg.read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.single_regfile.single_reg.read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.single_regfile.single_reg.read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.single_regfile.single_reg.write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.single_regfile.single_reg.write(0)
            write_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.single_regfile.single_reg.write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.single_regfile.single_reg.write(-1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.single_reg.write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.single_regfile.reg_array[0]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.single_regfile.reg_array[0].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[0].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.single_regfile.reg_array[0].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.single_regfile.reg_array[0].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.single_regfile.reg_array[0].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.single_regfile.reg_array[0].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.single_regfile.reg_array[0].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[0].write(-1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[0].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.single_regfile.reg_array[1]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.single_regfile.reg_array[1].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[1].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.single_regfile.reg_array[1].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.single_regfile.reg_array[1].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.single_regfile.reg_array[1].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.single_regfile.reg_array[1].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.single_regfile.reg_array[1].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[1].write(-1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[1].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.single_regfile.reg_array[2]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.single_regfile.reg_array[2].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[2].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.single_regfile.reg_array[2].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.single_regfile.reg_array[2].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.single_regfile.reg_array[2].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.single_regfile.reg_array[2].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.single_regfile.reg_array[2].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[2].write(-1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[2].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

        # test access operations (read and/or write) to register:
        # chip_with_registers.single_regfile.reg_array[3]
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
            patch(__name__ + '.' + 'read_addr_space', return_value=1) as read_callback_mock:

            # test reading back 1 (the unpatched version returns 0 so this confirms the patch works)
            self.assertEqual(self.dut.single_regfile.reg_array[3].read(), 1)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].accesswidth)

            # test the read check with high value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFFFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[3].read(), 0xFFFFFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].accesswidth)

            # test the read of the low value
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0
            self.assertEqual(self.dut.single_regfile.reg_array[3].read(), 0x0)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].accesswidth)

            # test the read of a random value
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = random_value
            self.assertEqual(self.dut.single_regfile.reg_array[3].read(), random_value)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            

            # test the write with high value
            self.dut.single_regfile.reg_array[3].write(0xFFFFFFFF)
            write_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].accesswidth,
                                data=0xFFFFFFFF)
            write_callback_mock.reset_mock()

            # test the write of a low value
            self.dut.single_regfile.reg_array[3].write(0)
            write_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].accesswidth,
                                data=0)
            write_callback_mock.reset_mock()

            # test the write of a random
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            self.dut.single_regfile.reg_array[3].write(random_value)
            write_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].accesswidth,
                                data=random_value)
            write_callback_mock.reset_mock()

            # test writting a value beyond the register range is blocked with an exception being raised
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[3].write(-1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[3].write(0xFFFFFFFF+1)

            # check the read has not been called in the write test
            read_callback_mock.assert_not_called()

    def test_int_field_read_and_write(self):
        """
        Check the ability to read and write to integer (non-eumn) fields
        """

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].single_reg.first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[0].single_reg.first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[0].single_reg.first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].single_reg.first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].single_reg.first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[0].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[0].reg_array[0].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[0].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[0].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[1].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[0].reg_array[1].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[1].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[1].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[2].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[0].reg_array[2].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[2].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[2].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[3].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[0].reg_array[3].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[3].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[0].reg_array[3].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].single_reg.first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[1].single_reg.first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[1].single_reg.first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].single_reg.first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].single_reg.first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[0].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[1].reg_array[0].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[0].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[0].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[1].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[1].reg_array[1].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[1].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[1].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[2].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[1].reg_array[2].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[2].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[2].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[3].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.regfile_array[1].reg_array[3].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[3].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.regfile_array[1].reg_array[3].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.single_reg.first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.single_regfile.single_reg.first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.single_regfile.single_reg.first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.single_regfile.single_reg.first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.single_regfile.single_reg.first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.single_regfile.single_reg.first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.single_reg.first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[0].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.single_regfile.reg_array[0].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.single_regfile.reg_array[0].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[0].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[0].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[1].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.single_regfile.reg_array[1].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.single_regfile.reg_array[1].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[1].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[1].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[2].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.single_regfile.reg_array[2].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.single_regfile.reg_array[2].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[2].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[2].first_field.write(-1)

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[3].first_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            

            # read back - zero, this is achieved by setting the register to inverse bitmask
            read_callback_mock.return_value = 0xFFFF0000
            self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.read(),
                             0)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].first_field.parent_register.accesswidth)

            # read back - max_value, this is achieved by setting the register to bitmask
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = 0xFFFF
            self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.read(),
                             0xFFFF)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].first_field.parent_register.accesswidth)

            # read back - random value
            read_callback_mock.reset_mock()
            random_value = random.randrange(0, 0xFFFFFFFF+1)
            read_callback_mock.return_value = random_value
            random_field_value = (random_value & 0xFFFF) >> 0
            self.assertEqual(self.dut.single_regfile.reg_array[3].first_field.read(),
                             random_field_value)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].first_field.parent_register.accesswidth)

            # at the end of the read tests the write should not have been called
            read_callback_mock.reset_mock()
            write_callback_mock.assert_not_called()
            # check the write
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            random_field_value = random.randrange(0, 0xFFFF + 1)
            for reg_base_value in [0, 0xFFFFFFFF, random_reg_value]:
                for field_value in [0, 0xFFFF, random_field_value]:
                    read_callback_mock.reset_mock()
                    write_callback_mock.reset_mock()
                    read_callback_mock.return_value = reg_base_value

                    self.dut.single_regfile.reg_array[3].first_field.write(field_value)

                    
                    read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].first_field.parent_register.accesswidth)
                    
                    write_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].first_field.parent_register.accesswidth,
                                data=(reg_base_value & 0xFFFF0000) | \
                                     (0xFFFF & (field_value << 0)))
                    

            # check invalid write values bounce
            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[3].first_field.write(0xFFFF + 1)

            with self.assertRaises(ValueError):
                self.dut.single_regfile.reg_array[3].first_field.write(-1)

    
    def test_enum_field_read_and_write(self):
        """
        Check the ability to read and write to enum fields
        """

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].single_reg.second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.read(),
                             self.dut.regfile_array[0].single_reg.second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].single_reg.second_field.read(),
                             self.dut.regfile_array[0].single_reg.second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[0].single_reg.second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[0].single_reg.second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].single_reg.second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].single_reg.second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=0,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].single_reg.second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[0].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.read(),
                             self.dut.regfile_array[0].reg_array[0].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[0].second_field.read(),
                             self.dut.regfile_array[0].reg_array[0].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[0].reg_array[0].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[0].reg_array[0].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[0].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[0].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=4,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[0].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[1].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.read(),
                             self.dut.regfile_array[0].reg_array[1].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[1].second_field.read(),
                             self.dut.regfile_array[0].reg_array[1].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[0].reg_array[1].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[0].reg_array[1].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[1].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[1].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=8,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[1].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[2].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.read(),
                             self.dut.regfile_array[0].reg_array[2].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[2].second_field.read(),
                             self.dut.regfile_array[0].reg_array[2].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[0].reg_array[2].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[0].reg_array[2].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[2].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[2].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=12,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[2].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[0].reg_array[3].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.read(),
                             self.dut.regfile_array[0].reg_array[3].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[0].reg_array[3].second_field.read(),
                             self.dut.regfile_array[0].reg_array[3].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[0].reg_array[3].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[0].reg_array[3].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[3].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[0].reg_array[3].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=16,
                                width=32,
                                accesswidth=self.dut.regfile_array[0].reg_array[3].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].single_reg.second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.read(),
                             self.dut.regfile_array[1].single_reg.second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].single_reg.second_field.read(),
                             self.dut.regfile_array[1].single_reg.second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[1].single_reg.second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[1].single_reg.second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].single_reg.second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].single_reg.second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=20,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].single_reg.second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[0].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.read(),
                             self.dut.regfile_array[1].reg_array[0].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[0].second_field.read(),
                             self.dut.regfile_array[1].reg_array[0].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[1].reg_array[0].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[1].reg_array[0].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[0].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[0].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=24,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[0].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[1].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.read(),
                             self.dut.regfile_array[1].reg_array[1].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[1].second_field.read(),
                             self.dut.regfile_array[1].reg_array[1].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[1].reg_array[1].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[1].reg_array[1].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[1].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[1].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=28,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[1].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[2].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.read(),
                             self.dut.regfile_array[1].reg_array[2].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[2].second_field.read(),
                             self.dut.regfile_array[1].reg_array[2].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[1].reg_array[2].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[1].reg_array[2].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[2].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[2].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=32,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[2].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.regfile_array[1].reg_array[3].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.read(),
                             self.dut.regfile_array[1].reg_array[3].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.regfile_array[1].reg_array[3].second_field.read(),
                             self.dut.regfile_array[1].reg_array[3].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.regfile_array[1].reg_array[3].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.regfile_array[1].reg_array[3].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[3].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.regfile_array[1].reg_array[3].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=36,
                                width=32,
                                accesswidth=self.dut.regfile_array[1].reg_array[3].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.single_reg.second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.single_regfile.single_reg.second_field.read(),
                             self.dut.single_regfile.single_reg.second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.single_regfile.single_reg.second_field.read(),
                             self.dut.single_regfile.single_reg.second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.single_regfile.single_reg.second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.single_regfile.single_reg.second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.single_reg.second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.single_reg.second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=64,
                                width=32,
                                accesswidth=self.dut.single_regfile.single_reg.second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[0].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.read(),
                             self.dut.single_regfile.reg_array[0].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[0].second_field.read(),
                             self.dut.single_regfile.reg_array[0].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.single_regfile.reg_array[0].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.single_regfile.reg_array[0].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[0].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[0].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=68,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[0].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[1].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.read(),
                             self.dut.single_regfile.reg_array[1].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[1].second_field.read(),
                             self.dut.single_regfile.reg_array[1].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.single_regfile.reg_array[1].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.single_regfile.reg_array[1].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[1].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[1].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=72,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[1].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[2].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.read(),
                             self.dut.single_regfile.reg_array[2].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[2].second_field.read(),
                             self.dut.single_regfile.reg_array[2].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.single_regfile.reg_array[2].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.single_regfile.reg_array[2].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[2].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[2].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=76,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[2].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

        # test access operations (read and/or write) to field:
        # chip_with_registers.single_regfile.reg_array[3].second_field
        with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock,\
            patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:

            
            # read back test# set the simulated read_back value to value1
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (0 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.read(),
                             self.dut.single_regfile.reg_array[3].second_field.enum_cls.value1)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].second_field.parent_register.accesswidth)
            # set the simulated read_back value to value2
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                              (0x30000 & (1 << 16 ))
            self.assertEqual(self.dut.single_regfile.reg_array[3].second_field.read(),
                             self.dut.single_regfile.reg_array[3].second_field.enum_cls.value2)
            read_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].second_field.parent_register.accesswidth)
            

            
            # check that other values of the field int
            # that don't appear in the enum generate an
            # error
            for field_value in range(0, 0x3+1):
                if field_value in [0, 1]:
                    # legal int value of the eunm so no test is needed
                    continue
                with self.assertRaises(ValueError):
                    read_callback_mock.reset_mock()
                    random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
                    read_callback_mock.return_value = (random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (field_value << 16))
                    decode_field_value = self.dut.single_regfile.reg_array[3].second_field.read()
            
            write_callback_mock.assert_not_called()
            

            
            enum_cls = self.dut.single_regfile.reg_array[3].second_field.enum_cls
            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[3].second_field.write(enum_cls.value1)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (0 << 16)))
            

            
            random_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
            read_callback_mock.reset_mock()
            write_callback_mock.reset_mock()
            read_callback_mock.return_value = random_reg_value

            self.dut.single_regfile.reg_array[3].second_field.write(enum_cls.value2)

            
            read_callback_mock.assert_called_once()
            

            write_callback_mock.assert_called_once_with(
                                addr=80,
                                width=32,
                                accesswidth=self.dut.single_regfile.reg_array[3].second_field.parent_register.accesswidth,
                                data=(random_reg_value & 0xFFFCFFFF) | \
                                     (0x30000 & (1 << 16)))
            

            
            

    def test_register_read_fields(self):
        """
        Walk the register map and check every register read_fields method
        """
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].single_reg
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[0].single_reg.second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[0].single_reg.first_field.read(),
                                      'second_field' : self.dut.regfile_array[0].single_reg.second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[0].single_reg.read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[0]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[0].reg_array[0].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[0].reg_array[0].first_field.read(),
                                      'second_field' : self.dut.regfile_array[0].reg_array[0].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[0].reg_array[0].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[1]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[0].reg_array[1].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[0].reg_array[1].first_field.read(),
                                      'second_field' : self.dut.regfile_array[0].reg_array[1].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[0].reg_array[1].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[2]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[0].reg_array[2].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[0].reg_array[2].first_field.read(),
                                      'second_field' : self.dut.regfile_array[0].reg_array[2].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[0].reg_array[2].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[3]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[0].reg_array[3].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[0].reg_array[3].first_field.read(),
                                      'second_field' : self.dut.regfile_array[0].reg_array[3].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[0].reg_array[3].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].single_reg
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[1].single_reg.second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[1].single_reg.first_field.read(),
                                      'second_field' : self.dut.regfile_array[1].single_reg.second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[1].single_reg.read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[0]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[1].reg_array[0].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[1].reg_array[0].first_field.read(),
                                      'second_field' : self.dut.regfile_array[1].reg_array[0].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[1].reg_array[0].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[1]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[1].reg_array[1].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[1].reg_array[1].first_field.read(),
                                      'second_field' : self.dut.regfile_array[1].reg_array[1].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[1].reg_array[1].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[2]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[1].reg_array[2].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[1].reg_array[2].first_field.read(),
                                      'second_field' : self.dut.regfile_array[1].reg_array[2].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[1].reg_array[2].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[3]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.regfile_array[1].reg_array[3].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.regfile_array[1].reg_array[3].first_field.read(),
                                      'second_field' : self.dut.regfile_array[1].reg_array[3].second_field.read()
                                    }

            self.assertDictEqual(self.dut.regfile_array[1].reg_array[3].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.single_reg
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.single_regfile.single_reg.second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.single_regfile.single_reg.first_field.read(),
                                      'second_field' : self.dut.single_regfile.single_reg.second_field.read()
                                    }

            self.assertDictEqual(self.dut.single_regfile.single_reg.read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[0]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.single_regfile.reg_array[0].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.single_regfile.reg_array[0].first_field.read(),
                                      'second_field' : self.dut.single_regfile.reg_array[0].second_field.read()
                                    }

            self.assertDictEqual(self.dut.single_regfile.reg_array[0].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[1]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.single_regfile.reg_array[1].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.single_regfile.reg_array[1].first_field.read(),
                                      'second_field' : self.dut.single_regfile.reg_array[1].second_field.read()
                                    }

            self.assertDictEqual(self.dut.single_regfile.reg_array[1].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[2]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.single_regfile.reg_array[2].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.single_regfile.reg_array[2].first_field.read(),
                                      'second_field' : self.dut.single_regfile.reg_array[2].second_field.read()
                                    }

            self.assertDictEqual(self.dut.single_regfile.reg_array[2].read_fields(),
                                 reference_read_fields)
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[3]
        # build up the register value with a random base value, overlaid with
        # a random value for each field
        rand_reg_value = random.randrange(0, 0xFFFFFFFF + 1)
        rand_field_value = random.randrange(0, 0xFFFF + 1)
        rand_reg_value = (rand_reg_value & 0xFFFF0000) | (rand_field_value << 0)
        
        
        rand_field_value = random.choice(list(self.dut.single_regfile.reg_array[3].second_field.enum_cls)).value
        rand_reg_value = (rand_reg_value & 0xFFFCFFFF) | (rand_field_value << 16)
        
        
        with patch(__name__ + '.' + 'read_addr_space', return_value=rand_reg_value):
            # the read_fields method gets a dictionary back
            # from the object with all the read back field
            # values
            reference_read_fields = { 
                                      'first_field' : self.dut.single_regfile.reg_array[3].first_field.read(),
                                      'second_field' : self.dut.single_regfile.reg_array[3].second_field.read()
                                    }

            self.assertDictEqual(self.dut.single_regfile.reg_array[3].read_fields(),
                                 reference_read_fields)

    def test_register_write_fields(self):
        """
        Walk the register map and check every register write_fields method
        """
        def write_field_cominbinations(reg, writable_fields):
            with patch(__name__ + '.' + 'write_addr_space') as write_callback_mock, \
                patch(__name__ + '.' + 'read_addr_space', return_value=0) as read_callback_mock:
                for num_parm in range(1, len(writable_fields) + 1):
                    for fields_to_write in combinations(writable_fields, num_parm):
                        kwargs = {}
                        expected_value = 0
                        for field_str in fields_to_write:
                            field = getattr(reg, field_str)
                            if hasattr(field, 'enum_cls'):
                                rand_enum_value = random.choice(list(field.enum_cls))
                                rand_field_value = rand_enum_value.value
                                kwargs[field_str] = rand_enum_value
                            else:
                                rand_field_value = random.randrange(0, field.max_value + 1)
                                kwargs[field_str] = rand_field_value

                            if field.msb == field.high:
                                expected_value = ( expected_value & field.inverse_bitmask ) | (rand_field_value << field.low)
                            elif field.msb == field.low:
                                expected_value = ( expected_value & field.inverse_bitmask ) | (self._reverse_bits(value=rand_field_value, number_bits=field.width) << field.low)
                            else:
                                raise RuntimeError('invalid msb/lsb high/low combination')

                        reg.write_fields(**kwargs)
                        write_callback_mock.assert_called_once_with(
                                addr=reg.address,
                                width=reg.width,
                                accesswidth=reg.accesswidth,
                                data=expected_value)
                        read_callback_mock.assert_called_once()
                        write_callback_mock.reset_mock()
                        read_callback_mock.reset_mock()
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].single_reg


        
        write_field_cominbinations(reg=self.dut.regfile_array[0].single_reg,
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[0]


        
        write_field_cominbinations(reg=self.dut.regfile_array[0].reg_array[0],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[1]


        
        write_field_cominbinations(reg=self.dut.regfile_array[0].reg_array[1],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[2]


        
        write_field_cominbinations(reg=self.dut.regfile_array[0].reg_array[2],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[0].reg_array[3]


        
        write_field_cominbinations(reg=self.dut.regfile_array[0].reg_array[3],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].single_reg


        
        write_field_cominbinations(reg=self.dut.regfile_array[1].single_reg,
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[0]


        
        write_field_cominbinations(reg=self.dut.regfile_array[1].reg_array[0],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[1]


        
        write_field_cominbinations(reg=self.dut.regfile_array[1].reg_array[1],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[2]


        
        write_field_cominbinations(reg=self.dut.regfile_array[1].reg_array[2],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.regfile_array[1].reg_array[3]


        
        write_field_cominbinations(reg=self.dut.regfile_array[1].reg_array[3],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.single_reg


        
        write_field_cominbinations(reg=self.dut.single_regfile.single_reg,
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[0]


        
        write_field_cominbinations(reg=self.dut.single_regfile.reg_array[0],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[1]


        
        write_field_cominbinations(reg=self.dut.single_regfile.reg_array[1],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[2]


        
        write_field_cominbinations(reg=self.dut.single_regfile.reg_array[2],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        
        
        # test read_fields to register:
        # chip_with_registers.single_regfile.reg_array[3]


        
        write_field_cominbinations(reg=self.dut.single_regfile.reg_array[3],
                                   writable_fields = [ 'first_field',
                                                       'second_field'
                                                       ])
        

    

    def test_adding_attributes(self):
        """
        Walk the address map and attempt to set a new value on each node

        The attribute name: cppkbrgmgeloagvfgjjeiiushygirh was randomly generated to be unlikely to
        every be a attribute name

        """
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].single_reg.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].single_reg.first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].single_reg.second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[0].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[0].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[0].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[1].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[1].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[1].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[2].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[2].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[2].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[3].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[3].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[0].reg_array[3].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].single_reg.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].single_reg.first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].single_reg.second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[0].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[0].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[0].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[1].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[1].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[1].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[2].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[2].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[2].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[3].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[3].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.regfile_array[1].reg_array[3].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.single_reg.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.single_reg.first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.single_reg.second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[0].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[0].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[0].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[1].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[1].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[1].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[2].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[2].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[2].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[3].cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[3].first_field.cppkbrgmgeloagvfgjjeiiushygirh = 1
        with self.assertRaises(AttributeError):
            self.dut.single_regfile.reg_array[3].second_field.cppkbrgmgeloagvfgjjeiiushygirh = 1

    

    

    

    

    def test_traversal_iterators(self):
        """
        Walk the address map and check that the iterators for each node as as expected
        """
            
        
        expected_readable_regs = [self.dut.regfile_array[0].single_reg, self.dut.regfile_array[0].reg_array[0], self.dut.regfile_array[0].reg_array[1], self.dut.regfile_array[0].reg_array[2], self.dut.regfile_array[0].reg_array[3],  ]
        readable_regs = []
        for readable_reg in self.dut.regfile_array[0].get_readable_registers(unroll=True):
            readable_regs.append(readable_reg)
        self.assertCountEqual(expected_readable_regs, readable_regs)
        
        expected_readable_regs = [self.dut.regfile_array[0].single_reg, self.dut.regfile_array[0].reg_array,  ]
        readable_regs = []
        for readable_reg in self.dut.regfile_array[0].get_readable_registers(unroll=False):
            readable_regs.append(readable_reg)
        self.assertCountEqual(expected_readable_regs, readable_regs)
    
            
        
        expected_writable_regs = [self.dut.regfile_array[0].single_reg, self.dut.regfile_array[0].reg_array[0], self.dut.regfile_array[0].reg_array[1], self.dut.regfile_array[0].reg_array[2], self.dut.regfile_array[0].reg_array[3],  ]
        writable_regs = []
        for writable_reg in self.dut.regfile_array[0].get_writable_registers(unroll=True):
            writable_regs.append(writable_reg)
        self.assertCountEqual(expected_writable_regs, writable_regs)
        
        expected_writable_regs = [self.dut.regfile_array[0].single_reg, self.dut.regfile_array[0].reg_array,  ]
        writable_regs = []
        for writable_reg in self.dut.regfile_array[0].get_writable_registers(unroll=False):
            writable_regs.append(writable_reg)
        self.assertCountEqual(expected_writable_regs, writable_regs)
    
            
        
        expected_sections = [ ]
        sections = []
        for section in self.dut.regfile_array[0].get_sections(unroll=True):
            sections.append(section)
        self.assertCountEqual(expected_sections, sections)
        
        expected_sections = [ ]
        sections = []
        for section in self.dut.regfile_array[0].get_sections(unroll=False):
            sections.append(section)
        self.assertCountEqual(expected_sections, sections)
    
        self.assertFalse(hasattr(self.dut.regfile_array[0], 'get_memories'))
            
                
                
        expected_writable_fields = [self.dut.regfile_array[0].single_reg.first_field, self.dut.regfile_array[0].single_reg.second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[0].single_reg.writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[0].single_reg.first_field, self.dut.regfile_array[0].single_reg.second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[0].single_reg.readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[0].reg_array[0].first_field, self.dut.regfile_array[0].reg_array[0].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[0].reg_array[0].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[0].reg_array[0].first_field, self.dut.regfile_array[0].reg_array[0].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[0].reg_array[0].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[0].reg_array[1].first_field, self.dut.regfile_array[0].reg_array[1].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[0].reg_array[1].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[0].reg_array[1].first_field, self.dut.regfile_array[0].reg_array[1].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[0].reg_array[1].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[0].reg_array[2].first_field, self.dut.regfile_array[0].reg_array[2].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[0].reg_array[2].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[0].reg_array[2].first_field, self.dut.regfile_array[0].reg_array[2].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[0].reg_array[2].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[0].reg_array[3].first_field, self.dut.regfile_array[0].reg_array[3].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[0].reg_array[3].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[0].reg_array[3].first_field, self.dut.regfile_array[0].reg_array[3].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[0].reg_array[3].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
            
        
        expected_readable_regs = [self.dut.regfile_array[1].single_reg, self.dut.regfile_array[1].reg_array[0], self.dut.regfile_array[1].reg_array[1], self.dut.regfile_array[1].reg_array[2], self.dut.regfile_array[1].reg_array[3],  ]
        readable_regs = []
        for readable_reg in self.dut.regfile_array[1].get_readable_registers(unroll=True):
            readable_regs.append(readable_reg)
        self.assertCountEqual(expected_readable_regs, readable_regs)
        
        expected_readable_regs = [self.dut.regfile_array[1].single_reg, self.dut.regfile_array[1].reg_array,  ]
        readable_regs = []
        for readable_reg in self.dut.regfile_array[1].get_readable_registers(unroll=False):
            readable_regs.append(readable_reg)
        self.assertCountEqual(expected_readable_regs, readable_regs)
    
            
        
        expected_writable_regs = [self.dut.regfile_array[1].single_reg, self.dut.regfile_array[1].reg_array[0], self.dut.regfile_array[1].reg_array[1], self.dut.regfile_array[1].reg_array[2], self.dut.regfile_array[1].reg_array[3],  ]
        writable_regs = []
        for writable_reg in self.dut.regfile_array[1].get_writable_registers(unroll=True):
            writable_regs.append(writable_reg)
        self.assertCountEqual(expected_writable_regs, writable_regs)
        
        expected_writable_regs = [self.dut.regfile_array[1].single_reg, self.dut.regfile_array[1].reg_array,  ]
        writable_regs = []
        for writable_reg in self.dut.regfile_array[1].get_writable_registers(unroll=False):
            writable_regs.append(writable_reg)
        self.assertCountEqual(expected_writable_regs, writable_regs)
    
            
        
        expected_sections = [ ]
        sections = []
        for section in self.dut.regfile_array[1].get_sections(unroll=True):
            sections.append(section)
        self.assertCountEqual(expected_sections, sections)
        
        expected_sections = [ ]
        sections = []
        for section in self.dut.regfile_array[1].get_sections(unroll=False):
            sections.append(section)
        self.assertCountEqual(expected_sections, sections)
    
        self.assertFalse(hasattr(self.dut.regfile_array[1], 'get_memories'))
            
                
                
        expected_writable_fields = [self.dut.regfile_array[1].single_reg.first_field, self.dut.regfile_array[1].single_reg.second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[1].single_reg.writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[1].single_reg.first_field, self.dut.regfile_array[1].single_reg.second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[1].single_reg.readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[1].reg_array[0].first_field, self.dut.regfile_array[1].reg_array[0].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[1].reg_array[0].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[1].reg_array[0].first_field, self.dut.regfile_array[1].reg_array[0].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[1].reg_array[0].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[1].reg_array[1].first_field, self.dut.regfile_array[1].reg_array[1].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[1].reg_array[1].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[1].reg_array[1].first_field, self.dut.regfile_array[1].reg_array[1].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[1].reg_array[1].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[1].reg_array[2].first_field, self.dut.regfile_array[1].reg_array[2].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[1].reg_array[2].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[1].reg_array[2].first_field, self.dut.regfile_array[1].reg_array[2].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[1].reg_array[2].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.regfile_array[1].reg_array[3].first_field, self.dut.regfile_array[1].reg_array[3].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.regfile_array[1].reg_array[3].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.regfile_array[1].reg_array[3].first_field, self.dut.regfile_array[1].reg_array[3].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.regfile_array[1].reg_array[3].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
            
        
        expected_readable_regs = [self.dut.single_regfile.single_reg, self.dut.single_regfile.reg_array[0], self.dut.single_regfile.reg_array[1], self.dut.single_regfile.reg_array[2], self.dut.single_regfile.reg_array[3],  ]
        readable_regs = []
        for readable_reg in self.dut.single_regfile.get_readable_registers(unroll=True):
            readable_regs.append(readable_reg)
        self.assertCountEqual(expected_readable_regs, readable_regs)
        
        expected_readable_regs = [self.dut.single_regfile.single_reg, self.dut.single_regfile.reg_array,  ]
        readable_regs = []
        for readable_reg in self.dut.single_regfile.get_readable_registers(unroll=False):
            readable_regs.append(readable_reg)
        self.assertCountEqual(expected_readable_regs, readable_regs)
    
            
        
        expected_writable_regs = [self.dut.single_regfile.single_reg, self.dut.single_regfile.reg_array[0], self.dut.single_regfile.reg_array[1], self.dut.single_regfile.reg_array[2], self.dut.single_regfile.reg_array[3],  ]
        writable_regs = []
        for writable_reg in self.dut.single_regfile.get_writable_registers(unroll=True):
            writable_regs.append(writable_reg)
        self.assertCountEqual(expected_writable_regs, writable_regs)
        
        expected_writable_regs = [self.dut.single_regfile.single_reg, self.dut.single_regfile.reg_array,  ]
        writable_regs = []
        for writable_reg in self.dut.single_regfile.get_writable_registers(unroll=False):
            writable_regs.append(writable_reg)
        self.assertCountEqual(expected_writable_regs, writable_regs)
    
            
        
        expected_sections = [ ]
        sections = []
        for section in self.dut.single_regfile.get_sections(unroll=True):
            sections.append(section)
        self.assertCountEqual(expected_sections, sections)
        
        expected_sections = [ ]
        sections = []
        for section in self.dut.single_regfile.get_sections(unroll=False):
            sections.append(section)
        self.assertCountEqual(expected_sections, sections)
    
        self.assertFalse(hasattr(self.dut.single_regfile, 'get_memories'))
            
                
                
        expected_writable_fields = [self.dut.single_regfile.single_reg.first_field, self.dut.single_regfile.single_reg.second_field,  ]
        writable_fields = []
        for writable_field in self.dut.single_regfile.single_reg.writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.single_regfile.single_reg.first_field, self.dut.single_regfile.single_reg.second_field,  ]
        readable_fields = []
        for readable_field in self.dut.single_regfile.single_reg.readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.single_regfile.reg_array[0].first_field, self.dut.single_regfile.reg_array[0].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.single_regfile.reg_array[0].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.single_regfile.reg_array[0].first_field, self.dut.single_regfile.reg_array[0].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.single_regfile.reg_array[0].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.single_regfile.reg_array[1].first_field, self.dut.single_regfile.reg_array[1].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.single_regfile.reg_array[1].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.single_regfile.reg_array[1].first_field, self.dut.single_regfile.reg_array[1].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.single_regfile.reg_array[1].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.single_regfile.reg_array[2].first_field, self.dut.single_regfile.reg_array[2].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.single_regfile.reg_array[2].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.single_regfile.reg_array[2].first_field, self.dut.single_regfile.reg_array[2].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.single_regfile.reg_array[2].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                
                
                
        expected_writable_fields = [self.dut.single_regfile.reg_array[3].first_field, self.dut.single_regfile.reg_array[3].second_field,  ]
        writable_fields = []
        for writable_field in self.dut.single_regfile.reg_array[3].writable_fields:
            writable_fields.append(writable_field)
        self.assertCountEqual(expected_writable_fields, writable_fields)
                
                
        expected_readable_fields = [self.dut.single_regfile.reg_array[3].first_field, self.dut.single_regfile.reg_array[3].second_field,  ]
        readable_fields = []
        for readable_field in self.dut.single_regfile.reg_array[3].readable_fields:
            readable_fields.append(readable_field)
        self.assertCountEqual(expected_readable_fields, readable_fields)
                

class chip_with_registers_TestCase_BlockAccess(unittest.TestCase):

    def setUp(self):
        self.dut = chip_with_registers_cls(CallbackSet(read_callback=read_callback,
                                                          write_callback=write_callback,
                                                          read_block_callback=read_block_callback,
                                                          write_block_callback=write_block_callback))

    


if __name__ == '__main__':
    unittest.main()



