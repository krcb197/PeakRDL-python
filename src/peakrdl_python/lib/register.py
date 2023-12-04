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
from enum import Enum
from typing import List, Union, Iterator, TYPE_CHECKING, Tuple, cast, Optional, Dict, TypeVar, Type
from typing import Generator
from abc import ABC, abstractmethod
from contextlib import contextmanager
from array import array as Array
import sys

from .base import Node, AddressMap, RegFile, NodeArray, get_array_typecode
from .base import AsyncAddressMap, AsyncRegFile
from .memory import  MemoryReadOnly, MemoryWriteOnly, MemoryReadWrite, \
    BaseMemory, Memory, ReadableMemory, WritableMemory
from .callbacks import NormalCallbackSet

# pylint: disable=duplicate-code
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self
# pylint: enable=duplicate-code

if TYPE_CHECKING:
    from .fields import FieldReadOnly, FieldWriteOnly, FieldReadWrite

# pylint: disable=redefined-slots-in-subclass,too-many-lines


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
        if width not in (8, 16, 32, 64, 128, 256, 512, 1024, 2048):
            raise ValueError('currently only support 8, 16, 32, 64, 128, 256, 512, 1024 or 2048 '
                             f'width registers, got {width:d}')
        self.__width = width
        if not isinstance(accesswidth, int):
            raise TypeError(f'accesswidth should be int but got {(type(accesswidth))}')
        if accesswidth not in (8, 16, 32, 64):
            raise ValueError(f'currently only support 8, 16, 32 or 64 accesswidth, got {width:d}')
        self.__accesswidth = accesswidth
    # pylint: enable=too-many-arguments,duplicate-code

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the register

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

        Returns: register width

        """
        return self.__width

    @property
    def accesswidth(self) -> int:
        """
        The access width of the register in bits, this uses the `accesswidth` systemRDL property

        Returns: register access width
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

class Reg(BaseReg, ABC):
    """
        base class of non-async register wrappers

        Note:
            It is not expected that this class will be instantiated under normal
            circumstances however, it is useful for type checking
        """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, Memory, 'RegArray']):

        if not isinstance(parent, (AddressMap, RegFile,
                                   MemoryReadOnly, MemoryWriteOnly, MemoryReadWrite, RegArray)):
            raise TypeError(f'bad parent type got: {type(parent)}')

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(address=address, width=width, accesswidth=accesswidth,
                         logger_handle=logger_handle, inst_name=inst_name, parent=parent)

    @property
    def _callbacks(self) -> NormalCallbackSet:
        if self.parent is None:
            raise RuntimeError('Parent must be set')
        # This cast is OK because the type was checked in the __init__
        # pylint: disable-next=protected-access
        return cast(NormalCallbackSet, self.parent._callbacks)


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
        if width not in (8, 16, 32, 64, 128, 256, 512, 1024, 2048):
            raise ValueError('currently only support 8, 16, 32, 64, 128, 256, 512, 1024 or 2048 '
                             f'width registers, got {width:d}')
        self.__width = width
        if not isinstance(accesswidth, int):
            raise TypeError(f'accesswidth should be int but got {(type(accesswidth))}')
        if accesswidth not in (8, 16, 32, 64):
            raise ValueError(f'currently only support 8, 16, 32 or 64 accesswidth, got {width:d}')
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

        Returns: register width

        """
        return self.__width

    @property
    def accesswidth(self) -> int:
        """
        The access width of the register in bits, this uses the `accesswidth` systemRDL property

        Returns: register access width
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


# pylint: disable-next=invalid-name
RegArrayElementType= TypeVar('RegArrayElementType', bound=Reg)


class RegArray(BaseRegArray, ABC):
    """
    base class of register array wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    # pylint: disable=too-many-arguments,duplicate-code

    __slots__: List[str] = ['__in_context_manager', '__register_array_cache',
                            '__register_address_array']

    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[AddressMap, RegFile, Memory],
                 width: int,
                 accesswidth: int,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegArrayElementType]] = None):

        self.__in_context_manager: bool = False
        self.__register_array_cache: Optional[Array] = None
        self.__register_address_array: Optional[List[int]] = None

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address, width=width, accesswidth=accesswidth,
                         stride=stride, dimensions=dimensions, elements=elements)

    @property
    def __empty_array_cache(self) -> Array:
        empty_array = [0 for _ in range(self.__number_cache_entries)]
        return Array(get_array_typecode(self.width), empty_array)

    def __block_read(self) -> Array:
        """
        Read all the contents of the array in the most optimal way, ideally with a block operation
        """
        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            data_read = \
                read_block_callback(addr=self.address,  # type: ignore[call-arg]
                                    width=self.width,  # type: ignore[call-arg]
                                    accesswidth=self.accesswidth,  # type: ignore[call-arg]
                                    length=self.__number_cache_entries)  # type: ignore[call-arg]

            if not isinstance(data_read, Array):
                raise TypeError('The read block callback is expected to return an array')

            return data_read

        if read_callback is not None:
            # there is not read_block_callback defined so we must used individual read
            data_array = self.__empty_array_cache

            if self.__register_address_array is None:
                raise RuntimeError('This address array has not be initialised')

            for entry,address in enumerate(self.__register_address_array):

                # python 3.7 doesn't have the callback defined as protocol so mypy doesn't
                # recognise the arguments in the call back functions
                data_entry = read_callback(addr=address,  # type: ignore[call-arg]
                                           width=self.width,  # type: ignore[call-arg]
                                           accesswidth=self.accesswidth)  # type: ignore[call-arg]

                data_array[entry] = data_entry

            return data_array

        raise RuntimeError('There is no usable callback')

    def __block_write(self, data: Array, verify: bool) -> None:
        """
        Write all the contents of the array in the most optimal way, ideally with a block operation
        """
        write_block_callback = self._callbacks.write_block_callback
        write_callback = self._callbacks.write_callback

        if write_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            write_block_callback(addr=self.address,  # type: ignore[call-arg]
                                 width=self.width,  # type: ignore[call-arg]
                                 accesswidth=self.width,  # type: ignore[call-arg]
                                 data=data)  # type: ignore[call-arg]

        elif write_callback is not None:
            # there is not write_block_callback defined so we must used individual write

            if self.__register_address_array is None:
                raise RuntimeError('This address array has not be initialised')

            for entry_index, entry_data in enumerate(data):
                entry_address = self.__register_address_array[entry_index]
                # python 3.7 doesn't have the callback defined as protocol so mypy doesn't
                # recognise the arguments in the call back functions
                write_callback(addr=entry_address,  # type: ignore[call-arg]
                               width=self.width,  # type: ignore[call-arg]
                               accesswidth=self.accesswidth,  # type: ignore[call-arg]
                               data=entry_data)  # type: ignore[call-arg]

        else:
            raise RuntimeError('No suitable callback')

        if verify:
            read_back_verify_data = self.__block_read()
            if read_back_verify_data != data:
                raise RegisterWriteVerifyError('Read back block miss-match')

    def __cache_entry(self, addr: int, width: int, accesswidth: int) -> int:
        """
        Validate the data provided and determine the cache entry

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits

        Returns: cache entry

        """
        if not isinstance(width, int):
            raise TypeError(f'Width should be an int byt got {type(width)}')
        if width != self.width:
            raise ValueError('Requested Read width does not match the expected value')
        if not isinstance(accesswidth, int):
            raise TypeError(f'accesswidth should be an int byt got {type(accesswidth)}')
        if accesswidth != self.accesswidth:
            raise ValueError('Requested Read accesswidth does not match the expected value')
        if not isinstance(addr, int):
            raise TypeError(f'addr should be an int byt got {type(addr)}')
        if not self.address <= addr < (self.address + self.size):
            raise ValueError(f'Requested address 0x{addr:X} is out of range 0x{self.address:X} to '
                             f'0x{self.address + self.size - (self.width >> 3):X}')
        cache_entry = (addr - self.address) // (self.width >> 3)
        if self.__register_address_array is None:
            raise RuntimeError('The address table should always be populated here')
        if self.__register_address_array[cache_entry] != addr:
            raise RuntimeError(f'The calculated cache entry for address 0x{addr:X}')
        return cache_entry

    def __cache_read(self, addr: int, width: int, accesswidth: int) -> int:
        """
        Used to replace the normal callbacks with those that access the cache

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits

        Returns:
            value inputted by the used
        """
        if self.__register_array_cache is None:
            raise RuntimeError('The cache array should be initialised')
        return self.__register_array_cache[self.__cache_entry(addr=addr,
                                                              width=width,
                                                              accesswidth=accesswidth)]



    def __cache_write(self, addr: int, width: int, accesswidth: int, data: int) -> None:
        """
        Used to replace the normal callbacks with those that access the cache

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits
            data: value to be written to the register

        Returns:
            None
        """
        if not isinstance(data, int):
            raise TypeError(f'Data should be an int byt got {type(data)}')
        if self.__register_array_cache is None:
            raise RuntimeError('The cache array should be initialised')
        self.__register_array_cache[self.__cache_entry(addr=addr,
                                                       width=width,
                                                       accesswidth=accesswidth)] = data


    @property
    def __cache_callbacks(self) -> NormalCallbackSet:
        return NormalCallbackSet(read_callback=self.__cache_read,
                                 write_callback=self.__cache_write)


    @property
    def __number_cache_entries(self) -> int:
        return self.size // (self.width >> 3)

    @contextmanager
    def _cached_access(self, verify: bool = False, skip_write: bool = False,
                                   skip_initial_read: bool = False) -> \
            Generator[Self, None, None]:
        """
        Context manager to allow multiple field reads/write to be done with a single set of
        field operations

        Args:
            verify (bool): very the write with a read afterwards
            skip_write (bool): skip the write back at the end

        Returns:

        """
        self.__register_address_array = \
            [self.address + (i * (self.width >> 3)) for i in range(self.__number_cache_entries)]
        if skip_initial_read:
            self.__register_array_cache = self.__empty_array_cache
        else:
            self.__register_array_cache = self.__block_read()
        self.__in_context_manager = True
        yield self
        self.__in_context_manager = False
        if not skip_write:
            self.__block_write(self.__register_array_cache, verify)

        # clear the register states at the end of the context manager
        self.__register_address_array = None
        self.__register_array_cache = None

    @property
    def _callbacks(self) -> NormalCallbackSet:

        if self.__in_context_manager:
            return self.__cache_callbacks

        if self.parent is None:
            raise RuntimeError('Parent must be set')
        # This cast is OK because the type was checked in the __init__
        # pylint: disable-next=protected-access
        return cast(NormalCallbackSet, self.parent._callbacks)

class RegReadOnly(Reg, ABC):
    """
    class for a read only register

    Args:
        callbacks: set of callback to be used for accessing the hardware or simulator
        address: address of the register
        width: width of the register in bits
        accesswidth: minimum access width of the register in bits
        logger_handle: name to be used logging messages associate with this
            object

    """

    __slots__: List[str] = ['__in_context_manager', '__register_state']

    # pylint: disable=too-many-arguments, duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, ReadableMemory]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)

        self.__in_context_manager: bool = False
        self.__register_state: int = 0

    # pylint: enable=too-many-arguments, duplicate-code

    @contextmanager
    def single_read(self) -> Generator[Self, None, None]:
        """
        Context manager to allow multiple field accesses to be performed with a single
        read of the register

        Returns:

        """
        self.__register_state = self.read()
        self.__in_context_manager = True
        yield self
        self.__in_context_manager = False

    def read(self) -> int:
        """Read value from the register

        Returns:
            The value from register

        """
        if self.__in_context_manager:
            return self.__register_state

        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            return read_callback(addr=self.address,  # type: ignore[call-arg]
                                 width=self.width,  # type: ignore[call-arg]
                                 accesswidth=self.accesswidth)  # type: ignore[call-arg]

        if read_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            return read_block_callback(addr=self.address,  # type: ignore[call-arg]
                                       width=self.width,  # type: ignore[call-arg]
                                       accesswidth=self.accesswidth,  # type: ignore[call-arg]
                                       length=1)[0]  # type: ignore[call-arg]

        raise RuntimeError('This function does not have a useable callback')

    @property
    @abstractmethod
    def readable_fields(self) -> Iterator[Union['FieldReadOnly', 'FieldReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """

    def read_fields(self) -> Dict['str', Union[bool, Enum, int]]:
        """
        read the register and return a dictionary of the field values
        """
        return_dict: Dict['str', Union[bool, Enum, int]] = {}
        with self.single_read() as reg:
            for field in reg.readable_fields:
                return_dict[field.inst_name] = field.read()

        return return_dict

    @property
    def _is_readable(self) -> bool:
        # pylint: disable=duplicate-code
        return True

    @property
    def _is_writeable(self) -> bool:
        # pylint: disable=duplicate-code
        return False


class RegWriteOnly(Reg, ABC):
    """
    class for a write only register
    """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments, duplicate-code, useless-parent-delegation
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, WritableMemory]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)
    # pylint: enable=too-many-arguments, duplicate-code

    def write(self, data: int) -> None:
        """Writes a value to the register

        Args:
            data: data to be written

        Raises:
            ValueError: if the value provided is outside the range of the
                permissible values for the register
            TypeError: if the type of data is wrong
        """
        # this method check the types and range checks the data
        self._validate_data(data=data)

        self._logger.info('Writing data:%X to %X', data, self.address)

        block_callback = self._callbacks.write_block_callback
        single_callback = self._callbacks.write_callback

        if single_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            single_callback(addr=self.address,  # type: ignore[call-arg]
                            width=self.width,  # type: ignore[call-arg]
                            accesswidth=self.accesswidth,  # type: ignore[call-arg]
                            data=data)  # type: ignore[call-arg]

        elif block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            data_as_array = Array(get_array_typecode(self.width), [data])
            block_callback(addr=self.address,  # type: ignore[call-arg]
                           width=self.width,  # type: ignore[call-arg]
                           accesswidth=self.accesswidth,  # type: ignore[call-arg]
                           data=data_as_array)  # type: ignore[call-arg]

        else:
            raise RuntimeError('This function does not have a useable callback')

    @property
    @abstractmethod
    def writable_fields(self) -> Iterator[Union['FieldWriteOnly', 'FieldReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """

    @abstractmethod
    def write_fields(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """
        Do a write to the register, updating any field included in
        the arguments
        """

    @property
    def _is_readable(self) -> bool:
        # pylint: disable=duplicate-code
        return False

    @property
    def _is_writeable(self) -> bool:
        # pylint: disable=duplicate-code
        return True


class RegReadWrite(RegReadOnly, RegWriteOnly, ABC):
    """
    class for a read and write only register

    """
    __slots__: List[str] = ['__in_context_manager', '__register_state']

    # pylint: disable=too-many-arguments, duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, MemoryReadWrite]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)

        self.__in_context_manager: bool = False
        self.__register_state: Optional[int] = None

    # pylint: enable=too-many-arguments, duplicate-code

    @contextmanager
    def single_read_modify_write(self, verify: bool = False, skip_write: bool = False) -> \
            Generator[Self, None, None]:
        """
        Context manager to allow multiple field reads/write to be done with a single set of
        field operations

        Args:
            verify (bool): very the write with a read afterwards
            skip_write (bool): skip the write back at the end

        Returns:

        """
        self.__register_state = self.read()
        self.__in_context_manager = True
        yield self
        self.__in_context_manager = False
        if not skip_write:
            self.write(self.__register_state, verify)

        # clear the register states at the end of the context manager
        self.__register_state = None

    def write(self, data: int, verify: bool = False) -> None:  # pylint: disable=arguments-differ
        """
        Writes a value to the register

        Args:
            data: data to be written
            verify: set to True to read back the register to verify the read has occurred correctly

        Raises:
            ValueError: if the value provided is outside the range of the
                        permissible values for the register
            TypeError: if the type of data is wrong
            RegisterWriteVerifyError: the read back data after the write does not match the
                                      expected value
        """
        if self.__in_context_manager:
            if self.__register_state is None:
                raise RuntimeError('The internal register state should never be None in the '
                                   'context manager')
            self.__register_state = data
        else:
            super().write(data)
            if verify:
                read_back = self.read()
                if read_back != data:
                    raise RegisterWriteVerifyError(f'Readback {read_back:X} '
                                                   f'after writing {data:X}')

    def read(self) -> int:
        """Read value from the register

        Returns:
            The value from register
        """
        if self.__in_context_manager:
            if self.__register_state is None:
                raise RuntimeError('The internal register state should never be None in the '
                                   'context manager')
            return self.__register_state

        return super().read()

    def write_fields(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """
        if len(kwargs) == 0:
            raise ValueError('no command args')

        with self.single_read_modify_write() as reg:
            for field_name, field_value in kwargs.items():
                if field_name not in reg.systemrdl_python_child_name_map.values():
                    raise ValueError(f'{field_name} is not a member of the register')

                field = getattr(reg, field_name)
                field.write(field_value)

    def read_fields(self) -> Dict['str', Union[bool, Enum, int]]:
        """
        read the register and return a dictionary of the field values
        """
        return_dict: Dict['str', Union[bool, Enum, int]] = {}
        with self.single_read_modify_write(skip_write=True) as reg:
            for field in reg.readable_fields:
                return_dict[field.inst_name] = field.read()

        return return_dict

    @property
    def _is_readable(self) -> bool:
        # pylint: disable=duplicate-code
        return True

    @property
    def _is_writeable(self) -> bool:
        # pylint: disable=duplicate-code
        return True

ReadableRegister = Union[RegReadOnly, RegReadWrite]
WritableRegister = Union[RegWriteOnly, RegReadWrite]

class RegReadOnlyArray(RegArray, ABC):
    """
    base class for a array of read only registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, ReadableMemory],
                 address: int,
                 width: int,
                 accesswidth: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegReadOnly]] = None):

        if not isinstance(parent, (RegFile, AddressMap, MemoryReadOnly, MemoryReadWrite)):
            raise TypeError('parent should be either RegFile, AddressMap, '
                            'MemoryReadOnly, MemoryReadWrite '
                            f'got {type(parent)}')

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address, width=width, accesswidth=accesswidth,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code

    @contextmanager
    def single_read(self) -> \
            Generator[Self, None, None]:
        """
        Context manager to allow multiple field reads/write to be done with a single set of
        field operations

        Args:


        Returns:

        """
        with self._cached_access(verify=False, skip_write=True,
                                 skip_initial_read=False) as reg_array:
            yield reg_array

    @property
    def _is_readable(self) -> bool:
        # pylint: disable=duplicate-code
        return True

    @property
    def _is_writeable(self) -> bool:
        # pylint: disable=duplicate-code
        return False

class RegWriteOnlyArray(RegArray, ABC):
    """
    base class for a array of write only registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, WritableMemory],
                 address: int,
                 width: int,
                 accesswidth: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegWriteOnly]] = None):

        if not isinstance(parent, (RegFile, AddressMap, MemoryWriteOnly, MemoryReadWrite)):
            raise TypeError('parent should be either RegFile, AddressMap, MemoryWriteOnly, '
                            'MemoryReadWrite '
                            f'got {type(parent)}')

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address, width=width, accesswidth=accesswidth,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code

    @contextmanager
    def single_write(self) -> \
            Generator[Self, None, None]:
        """
        Context manager to allow multiple field reads/write to be done with a single set of
        field operations

        Args:


        Returns:

        """
        with self._cached_access(verify=False, skip_write=False,
                                  skip_initial_read=True) as reg_array:
            yield reg_array

    @property
    def _is_readable(self) -> bool:
        # pylint: disable=duplicate-code
        return False

    @property
    def _is_writeable(self) -> bool:
        # pylint: disable=duplicate-code
        return True


class RegReadWriteArray(RegArray, ABC):
    """
    base class for a array of read and write registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, MemoryReadWrite],
                 address: int,
                 width: int,
                 accesswidth: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegReadWrite]] = None):

        if not isinstance(parent, (RegFile, AddressMap, MemoryReadWrite)):
            raise TypeError('parent should be either RegFile, AddressMap, MemoryReadWrite '
                            f'got {type(parent)}')

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address, width=width, accesswidth=accesswidth,
                         stride=stride, dimensions=dimensions, elements=elements)


    # pylint: enable=too-many-arguments,duplicate-code

    @contextmanager
    def single_read_modify_write(self, verify: bool = False, skip_write: bool = False) -> \
            Generator[Self, None, None]:
        """
        Context manager to allow multiple field reads/write to be done with a single set of
        field operations

        Args:
            verify (bool): very the write with a read afterwards
            skip_write (bool): skip the write back at the end

        Returns:

        """
        with self._cached_access(verify=verify, skip_write=skip_write,
                                  skip_initial_read=False) as reg_array:
            yield reg_array

    @property
    def _is_readable(self) -> bool:
        # pylint: disable=duplicate-code
        return True

    @property
    def _is_writeable(self) -> bool:
        # pylint: disable=duplicate-code
        return True


ReadableRegisterArray = Union[RegReadOnlyArray, RegReadWriteArray]
WriteableRegisterArray = Union[RegWriteOnlyArray, RegReadWriteArray]
