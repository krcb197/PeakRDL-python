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
from typing import Union, TypeVar, TYPE_CHECKING
from enum import Enum, EnumMeta
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field as dataclass_field


from ..lib import Field
from ..lib import AsyncReg, Reg
from ..lib.base_register import BaseReg
from ..lib.utility_functions import calculate_bitmask
from ..lib import FieldEnum

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
        return reg_value_for_field_read(fut=fut,
                                        reg_base_value=reg_base_value,
                                        field_value=field_value)

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

def random_int_field_value(fut: Field) -> int:
    """
    Return a random integer value within the legal range for a field
    """
    return random.randint(0, fut.max_value)

# The following line should be:
# FieldType = TypeVar('FieldType', bound=int|IntEnum|SystemRDLEnum)
# However, python 3.9 does not support the combination so the binding was removed
# pylint: disable-next=invalid-name
FieldType = TypeVar('FieldType')
def random_encoded_field_value(fut: FieldEnum[FieldType]) -> FieldType:
    """
    Return a random encoded values within the legal range for a field
    """
    # pylint:disable-next=invalid-name
    FieldEnumType = fut.enum_cls
    if TYPE_CHECKING:
        assert isinstance(FieldEnumType, EnumMeta)
    return random.choice(list(FieldEnumType))

def random_field_parent_reg_value(fut: Field) -> int:
    """
    Return a random integer values within the legal range for a field's register parent
    """
    # this needs a mypy ignore because the parent type of the register is not defined at the
    # field level, as it can be sync or async
    return random.randint(0, fut.parent_register.max_value)  # type: ignore[attr-defined]

def random_reg_value(rut: BaseReg) -> int:
    """
    Returns a random register value (note that this value may not have legal field decodes)
    """
    return random.randint(0, rut.max_value)

@dataclass()
class RandomReg:
    """
    Instance for testing a sequence of operations that occur when a register is written too,
    starting with a random register value.
    """
    rut: Union[AsyncReg, Reg]
    value: int = dataclass_field(init=False)

    def __post_init__(self) -> None:
        end_value, _ = self._random_legal_values(initial_value=random_reg_value(rut=self.rut),
                                                 field_iter=self.rut.fields)
        self.value = end_value

    def _random_legal_values(self, initial_value:int ,field_iter: Iterable[Field]) -> tuple[
        int, dict[str, Union[int, Enum]]]:
        """
        Returns a random register value, based on legal values for the fields within the register
        """

        # build up a register value, starting with a random register value
        reg_value = initial_value
        reg_field_content: dict[str, Union[int, Enum]] = {}
        for field in field_iter:
            if isinstance(field, FieldEnum):
                field_value_enum = random_encoded_field_value(field)
                reg_value = reg_value_for_field_read(
                    fut=field,
                    reg_base_value=reg_value,
                    field_value=field_value_enum.value)
                reg_field_content[field.inst_name] = field_value_enum
            else:
                field_value_int = random_int_field_value(field)
                reg_value = reg_value_for_field_read(
                    fut=field,
                    reg_base_value=reg_value,
                    field_value=field_value_int)
                reg_field_content[field.inst_name] = field_value_int

        return reg_value, reg_field_content

@dataclass()
class RegWriteTestSequence(RandomReg):
    """
    Instance for testing a sequence of operations that occur when a register is written too,
    starting with a random register value.
    """
    fields: Iterable[Field]
    start_value: int = dataclass_field(init=False)
    write_sequence: dict[str, Union[int, Enum]] = dataclass_field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.start_value = self.value
        self.value, self.write_sequence = self._random_legal_values(initial_value=self.start_value,
                                                                    field_iter=self.fields)


def get_field_bitmask_int(field: Field) -> int:
    """
    Integer bitmask for a field

    Args:
        field: node to be analysed

    Returns:
        bitmask as a string prefixed by 0x

    """
    return calculate_bitmask(high=field.high, low=field.low)

def get_field_inv_bitmask(field: Field) -> str:
    """
     Integer inverse bitmask for a field

    Args:
        field: node to be analysed

    Returns:
        inverse bitmask as a string prefixed by 0x

    """
    reg_max_value = field.parent_register.max_value  # type: ignore[attr-defined]
    return reg_max_value ^ get_field_bitmask_int(field)
