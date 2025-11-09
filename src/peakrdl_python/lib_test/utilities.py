"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This package It provide methods used by the tests
"""
import random

from ..lib import Field

def reverse_bits(value: int, number_bits: int) -> int:
    """
    reverse the order of bits in an integer

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

def expected_reg_write_data(fut: Field,
                            reg_base_value: int,
                            field_value: int,
                            readable_reg: bool) -> int:
    """
    Test utility function to generate the expected value to be write to a register, given a field
    update in the register

    Args:
        fut: Field being updated
        reg_base_value: register value before the write
        field_value: new field value
        readable_reg: is register readable

    Returns:

    """
    if readable_reg:
        expected_data = reg_base_value & fut.inverse_bitmask
        if fut.msb == fut.high:
            expected_data |= (fut.bitmask & (field_value << fut.low))
        else:
            expected_data |= (fut.bitmask & (reverse_bits(value=field_value,
                                                          number_bits=fut.width) << fut.low))

        return expected_data

    # if the register is not readable, the value is simply written
    if fut.msb == fut.high:
        return field_value << fut.low
    return reverse_bits(value=field_value, number_bits=fut.width) << fut.low

def reg_value_for_field_read(fut: Field,reg_base_value: int, field_value: int) -> int:
    """
    Return the register value that when a field read occurs will result in the field
    read providing a value of field_value
    """
    reg_value = reg_base_value & fut.inverse_bitmask
    if fut.msb == fut.high:
        return reg_value | fut.bitmask & (field_value << fut.low)

    return reg_value | fut.bitmask & (reverse_bits(value=field_value,
                                             number_bits=fut.width) << fut.low)

def reg_value_for_field_read_with_random_base(fut: Field, field_value: int) -> int:
    """
    Return the register value that when a field read occurs will result in the field
    read providing a value of field_value. With all other register bits being in a random
    state
    """
    return reg_value_for_field_read(
        fut=fut,
        field_value=field_value,
        reg_base_value=random_field_parent_reg_value(fut))

def random_field_value(fut: Field) -> int:
    """
    Return a random integer values within the legal range for a field
    """
    return random.randint(0, fut.max_value)

def random_field_parent_reg_value(fut: Field) -> int:
    """
    Return a random integer values within the legal range for a field's register parent
    """
    # this needs a mypy ignore because the parent type of the register is not defined at the
    # field level, as it can be sync or async
    return random.randint(0, fut.parent_register.max_value)  # type: ignore[attr-defined]
