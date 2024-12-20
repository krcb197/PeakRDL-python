"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2023

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

This module is intended to distributed as part of automatically generated code by the
peakrdl-python tool. It provides the base types for fields that are shared by non-async and async
fields
"""
from enum import EnumMeta
from typing import cast, Optional
from abc import ABC, abstractmethod

from .base import Base
from .utility_functions import swap_msb_lsb_ordering
from .base_register import BaseReg


class FieldSizeProps:
    """
    class to hold the key attributes of a field
    """
    __slots__ = ['__msb', '__lsb', '__width', '__high', '__low']

    # pylint: disable-next=too-many-arguments
    def __init__(self, *, width: int, msb: int, lsb: int, high: int, low: int):
        self.__width = width
        self.__msb = msb
        self.__lsb = lsb
        self.__high = high
        self.__low = low

        if self.width < 1:
            raise ValueError('width must be greater than 0')

        if self.high < self.low:
            raise ValueError('field high bit position can not be less than the '
                             'low bit position')

        if self.lsb < 0:
            raise ValueError('field low bit position cannot be less than zero')

    @property
    def lsb(self) -> int:
        """
        bit position of the least significant bit (lsb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__lsb

    @property
    def msb(self) -> int:
        """
        bit position of the most significant bit (msb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__msb

    @property
    def width(self) -> int:
        """
        The width of the field in bits
        """
        return self.__width

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the field

        For example:

        * 8-bit field returns 0xFF (255)
        * 16-bit field returns 0xFFFF (65535)
        * 32-bit field returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.width) - 1

    @property
    def high(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__high

    @property
    def low(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__low


class FieldMiscProps:
    """
    Class to hold additional attributes of a field
    """

    __slots__ = ['__default', '__is_volatile']

    def __init__(self, default:Optional[int], is_volatile:bool):
        self.__default = default
        self.__is_volatile = is_volatile

    @property
    def default(self) -> Optional[int]:
        """
        The default (reset) value of the field

        None
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        return self.__default

    @property
    def is_volatile(self) -> bool:
        """
        Volatility of the field. True if the field is hardware-writable.
        """
        return self.__is_volatile


class Field(Base, ABC):
    """
    base class of register field wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = ['__size_props', '__misc_props',
                 '__bitmask', '__msb0', '__lsb0']

    def __init__(self, *,
                 parent_register: BaseReg, size_props: FieldSizeProps, misc_props: FieldMiscProps,
                 logger_handle: str, inst_name: str):

        super().__init__(logger_handle=logger_handle,
                         inst_name=inst_name, parent=parent_register)

        if not isinstance(size_props, FieldSizeProps):
            raise TypeError(f'size_props must be of {type(FieldSizeProps)} '
                            f'but got {type(size_props)}')
        self.__size_props = size_props

        if not isinstance(misc_props, FieldMiscProps):
            raise TypeError(f'misc_props must be of {type(FieldMiscProps)} '
                            f'but got {type(misc_props)}')
        self.__misc_props = misc_props

        if not isinstance(parent_register, BaseReg):
            raise TypeError(f'parent_register must be of {type(BaseReg)} '
                            f'but got {type(parent_register)}')

        if self.width > self.register_data_width:
            raise ValueError('width can not be greater than parent width')

        if self.high > self.register_data_width:
            raise ValueError(f'field high bit position {self.high:d} must be less than the '
                             f'parent register width ({self.register_data_width:d})')

        if self.low > self.register_data_width:
            raise ValueError('field lsb must be less than the parent '
                             'register width')

        if self.high - self.low + 1 != self.width:
            raise ValueError('field width defined by lsb and msb does not match'
                             ' specified width')

        if (self.msb == self.high) and (self.lsb == self.low):
            self.__lsb0 = True
            self.__msb0 = False
        elif (self.msb == self.low) and (self.lsb == self.high):
            self.__lsb0 = False
            self.__msb0 = True
        else:
            raise ValueError('msb/lsb are inconsistent with low/high')

        self.__bitmask = 0
        for bit_position in range(self.low, self.high+1):
            self.__bitmask |= (1 << bit_position)

    @property
    def lsb(self) -> int:
        """
        bit position of the least significant bit (lsb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__size_props.lsb

    @property
    def msb(self) -> int:
        """
        bit position of the most significant bit (msb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__size_props.msb

    @property
    def width(self) -> int:
        """
        The width of the field in bits
        """
        return self.__size_props.width

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the field

        For example:

        * 8-bit field returns 0xFF (255)
        * 16-bit field returns 0xFFFF (65535)
        * 32-bit field returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.width) - 1

    @property
    def high(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__size_props.high

    @property
    def low(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__size_props.low

    @property
    def bitmask(self) -> int:
        """
        The bit mask needed to extract the field from its register

        For example a register field occupying bits 7 to 4 in a 16-bit register
        will have a bit mask of 0x00F0
        """
        return self.__bitmask

    @property
    def register_data_width(self) -> int:
        """
        The width of the register within which the field resides in bits
        """
        return self.__parent_register.width

    @property
    def inverse_bitmask(self) -> int:
        """
        The bitwise inverse of the bitmask needed to extract the field from its
        register

        For example a register field occupying bits 7 to 4 in a 16-bit register
        will have a inverse bit mask of 0xFF0F
        """
        return self.__parent_register.max_value ^ self.bitmask

    @property
    def msb0(self) -> bool:
        """
        The field can either be lsb0 or msb0

        Returns: true if msb0

        """
        return self.__msb0

    @property
    def lsb0(self) -> bool:
        """
        The field can either be lsb0 or msb0

        Returns: true if lsb0

        """
        return self.__lsb0

    @property
    def default(self) -> Optional[int]:
        """
        The default value of the field

        This returns None:
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        return self.__misc_props.default

    @property
    def is_volatile(self) -> bool:
        """
        The HW volatility of the field
        """
        return self.__misc_props.is_volatile

    @property
    def __parent_register(self) -> BaseReg:
        """
        parent register the field is placed in
        """
        # this cast is OK because an explict typing check was done in the __init__
        return cast(BaseReg, self.parent)


class _FieldReadOnlyFramework(Field, ABC):
    """
    base class for a async or normal read only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : list[str] = []

    def decode_read_value(self, value: int) -> int:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value
        """
        if not isinstance(value, int):
            raise TypeError(f'value must be an int but got {type(value)}')

        if value < 0:
            raise ValueError('value to be decoded must be greater '
                             'than or equal to 0')

        if value > self.__parent_register.max_value:
            raise ValueError(f'value to bede coded must be less than or equal '
                             f'to {self.__parent_register.max_value:d}')

        if self.msb0 is False:
            return_value = (value & self.bitmask) >> self.low
        else:
            return_value = swap_msb_lsb_ordering(value=(value & self.bitmask) >> self.low,
                                                 width=self.width)

        return return_value

    @property
    def __parent_register(self) -> BaseReg:
        """
        parent register the field is placed in
        """
        # this cast is OK because an explict typing check was done in the __init__
        return cast(BaseReg, self.parent)


class _FieldWriteOnlyFramework(Field, ABC):
    """
    class for a write only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : list[str] = []

    def _write_value_checks(self, value: int) -> None:
        """
        Carries out the value for the encode_write_value and write methods

        Args:
            value: proposed value to write
        """
        if not isinstance(value, int):
            raise TypeError(f'value must be an int but got {type(value)}')

        if value < 0:
            raise ValueError('value to be written to register must be greater '
                             'than or equal to 0')

        if value > self.max_value:
            raise ValueError(f'value to be written to register must be less '
                             f'than or equal to {self.max_value:d}')

    def encode_write_value(self, value: int) -> int:
        """
        Check that a value is legal for the field and then encode it in preparation to be written
        to the register

        Args:
            value: field value

        Returns:
            value which can be applied to the register to update the field

        """
        self._write_value_checks(value=value)

        if self.msb0 is False:
            return_value = value << self.low
        else:
            return_value = swap_msb_lsb_ordering(value=value,  width=self.width) << self.low

        return return_value


class FieldEnum(Field, ABC):
    """
    class for a register field with an enumerated value
    """
    __slots__: list[str] = []

    @property
    @abstractmethod
    def enum_cls(self) -> EnumMeta:
        """
        The enumeration class for this field
        """

    @property
    def _enum_values(self) -> list[int]:
        """
        provide the legal values for the enumeration
        """
        return [e.value for e in self.enum_cls] # type: ignore[var-annotated]
