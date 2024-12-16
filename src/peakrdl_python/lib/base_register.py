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
peakrdl-python tool. It provides a set of classes used by the autogenerated code to represent
registers
"""
from typing import List, Union, Tuple, Optional, Dict, TypeVar, Type
from abc import ABC, abstractmethod


from .base import Node, AddressMap, RegFile, NodeArray
from .utility_functions import legal_register_width
from .base import AsyncAddressMap, AsyncRegFile
from .memory import BaseMemory


class RegisterWriteVerifyError(Exception):
    """
    Exception that occurs when the read after a write does not match the expected value
    """


class BaseReg(Node, ABC):
    """
    base class of register wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = ['__width', '__accesswidth']

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, AsyncAddressMap, RegFile, AsyncRegFile, BaseMemory,
                               'BaseRegArray']):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)
        if not isinstance(width, int):
            raise TypeError(f'width should be int but got {(type(width))}')
        if not legal_register_width(width_in_bits=width):
            raise ValueError(f'Unsupported register width {width:d}')
        self.__width = width
        if not isinstance(accesswidth, int):
            raise TypeError(f'accesswidth should be int but got {(type(accesswidth))}')
        if not legal_register_width(width_in_bits=accesswidth):
            raise ValueError(f'Unsupported access width {accesswidth:d}')
        self.__accesswidth = accesswidth
    # pylint: enable=too-many-arguments,duplicate-code

    @property
    def max_value(self) -> int:
        """
        maximum unsigned integer value that can be stored in the register

        For example:

        * 8-bit register returns 0xFF (255)
        * 16-bit register returns 0xFFFF (65535)
        * 32-bit register returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.width) - 1

    def _validate_data(self, data: int) -> None:
        """
        Check that the data parameter is of valid type and range
        """
        if not isinstance(data, int):
            raise TypeError(f'data should be an int got {type(data)}')

        if data > self.max_value:
            raise ValueError('data out of range')

        if data < 0:
            raise ValueError('data out of range')

    @property
    def width(self) -> int:
        """
        The width of the register in bits, this uses the `regwidth` systemRDL property
        """
        return self.__width

    @property
    def accesswidth(self) -> int:
        """
        The access width of the register in bits, this uses the `accesswidth` systemRDL property
        """
        return self.__accesswidth

    @property
    def size(self) -> int:
        """
        Total Number of bytes of address the node occupies
        """
        return self.__width >> 3

    @property
    @abstractmethod
    def _is_readable(self) -> bool:
        ...

    @property
    @abstractmethod
    def _is_writeable(self) -> bool:
        ...

# pylint: disable-next=invalid-name
BaseRegArrayElementType= TypeVar('BaseRegArrayElementType', bound=BaseReg)


class BaseRegArray(NodeArray[BaseRegArrayElementType], ABC):
    """
    base class of register array wrappers (async and non-async)

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    # pylint: disable=too-many-arguments,duplicate-code

    __slots__: List[str] = ['__width', '__accesswidth']

    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[AddressMap, AsyncAddressMap, RegFile, AsyncRegFile, BaseMemory],
                 width: int,
                 accesswidth: int,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], BaseRegArrayElementType]] = None):

        if not isinstance(width, int):
            raise TypeError(f'width should be int but got {(type(width))}')
        if not legal_register_width(width_in_bits=width):
            raise ValueError(f'Unsupported register width {width:d}')
        self.__width = width
        if not isinstance(accesswidth, int):
            raise TypeError(f'accesswidth should be int but got {(type(accesswidth))}')
        if not legal_register_width(width_in_bits=accesswidth):
            raise ValueError(f'Unsupported access width {accesswidth:d}')
        self.__accesswidth = accesswidth

        if not issubclass(self._element_datatype, BaseReg):
            raise TypeError(f'{self._element_datatype}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions, elements=elements)

    @property
    def width(self) -> int:
        """
        The width of the register in bits, this uses the `regwidth` systemRDL property
        """
        return self.__width

    @property
    def accesswidth(self) -> int:
        """
        The access width of the register in bits, this uses the `accesswidth` systemRDL property
        """
        return self.__accesswidth

    def _build_element(self, indices: Tuple[int, ...]) -> BaseRegArrayElementType:

        return self._element_datatype(
            logger_handle=self._build_element_logger_handle(indices=indices),
            address=self._address_calculator(indices),
            inst_name=self._build_element_inst_name(indices=indices),
            width=self.width,
            accesswidth=self.accesswidth,
            parent=self)

    def _sub_instance(self, elements: Dict[Tuple[int, ...], BaseRegArrayElementType]) ->\
            NodeArray[BaseRegArrayElementType]:
        if not isinstance(self.parent, (AddressMap, AsyncAddressMap, RegFile,
                                        AsyncRegFile, BaseMemory)):
            raise RuntimeError('Parent of a Node Array must be Node')
        return self.__class__(logger_handle=self._logger.name,
                              inst_name=self.inst_name,
                              parent=self.parent,
                              address=self.address,
                              width=self.width,
                              accesswidth=self.accesswidth,
                              stride=self.stride,
                              dimensions=self.dimensions,
                              elements=elements)

    @property
    @abstractmethod
    def _element_datatype(self) -> Type[BaseRegArrayElementType]:
        ...

    @property
    @abstractmethod
    def _is_readable(self) -> bool:
        ...

    @property
    @abstractmethod
    def _is_writeable(self) -> bool:
        ...
