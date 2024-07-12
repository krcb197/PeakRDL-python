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
memories
"""
from array import array as Array
from typing import List, Union, Tuple, Iterator, TYPE_CHECKING
from abc import ABC, abstractmethod
import sys

from .base import Node, AddressMap, AsyncAddressMap, NodeArray
from .utility_functions import get_array_typecode

from .callbacks import NormalCallbackSet, NormalCallbackSetLegacy

# same bit of code exists in base so flags as duplicate
# pylint: disable=duplicate-code
if sys.version_info >= (3, 10):
    # type guarding was introduced in python 3.10
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard
# pylint: enable=duplicate-code


if TYPE_CHECKING:
    from .register import Reg, RegArray
    from .register import ReadableRegister, WritableRegister
    from .register import ReadableRegisterArray, WriteableRegisterArray
    from .async_memory import AsyncMemoryArray

# pylint: disable=duplicate-code


class BaseMemory(Node, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = ['__memwidth', '__entries', '__accesswidth']

    # pylint: disable=too-many-arguments
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, AsyncAddressMap, 'MemoryArray', 'AsyncMemoryArray']):
        """
        Initialise the class

        Args:
            callbacks: set of callback to be used for accessing the hardware or simulator
            address: address of the register
            width: width of the register in bits
            logger_handle: name to be used logging messages associate with thisobject
        """
        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        self.__memwidth = width
        self.__entries = entries
        self.__accesswidth = accesswidth
    # pylint: enable=too-many-arguments

    @property
    def width(self) -> int:
        """
        The width of the memory in bits, this uses the `memwidth` systemRDL property

        Returns: memory width

        """
        return self.__memwidth

    @property
    def width_in_bytes(self) -> int:
        """
        The width of the memory bytes, i.e. the width in bits divided by 8

        Returns: memory width (in bytes)

        """
        def roundup_pow2(x: int) -> int:
            return 1 << (x - 1).bit_length()

        return roundup_pow2(self.width) // 8

    @property
    def entries(self) -> int:
        """
        The number of entries in the memory, this uses the `mementries` systemRDL property

        Returns: memory entries

        """
        return self.__entries

    @property
    def array_typecode(self) -> str:
        """
        the python array.array type is initialised with a typecode. This property provides the
        recommended typecode to use with this class instance (based on the memwidth)

        Returns: typecode

        """
        return get_array_typecode(self.width)

    @property
    def size(self) -> int:
        """
        Total Number of bytes of address the node occupies
        """
        return self.entries * self.width_in_bytes

    def address_lookup(self, entry: int) -> int:
        """
        provides the address for an entry in the memory.

        Examples

        Args:
            entry: entry number to look up the address for

        Returns: Address

        """
        if not isinstance(entry, int):
            raise TypeError(f'entry must be an int but got {type(entry)}')

        if entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries-1:d} but got {entry:d}')

        return self.address + (entry * self.width_in_bytes)

    @property
    def accesswidth(self) -> int:
        """
        The access width of the register in bits, this uses the `accesswidth` systemRDL property

        Returns: register access width
        """
        return self.__accesswidth


class Memory(BaseMemory, ABC):
    """
    base class of non_async memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, 'MemoryArray']):
        """
        Initialise the class

        Args:
            callbacks: set of callback to be used for accessing the hardware or simulator
            address: address of the register
            width: width of the register in bits
            logger_handle: name to be used logging messages associate with thisobject
        """
        if not isinstance(parent, (AddressMap,
                                   MemoryWriteOnlyArray, MemoryReadOnlyArray,
                                   MemoryReadWriteArray)):
            raise TypeError(f'parent should be either AddressMap or Memory Array got '
                            f'{type(parent)}')
        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         width=width,
                         accesswidth=accesswidth,
                         entries=entries,
                         parent=parent)

    @abstractmethod
    def get_registers(self, unroll: bool = False) -> \
            Iterator[Union['Reg', 'RegArray']]:
        """
        generator that produces all the readable_registers of this node

        Args:
            unroll: Whether to unroll child array or not
        """


class _MemoryReadOnly(Memory, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments
    def __init__(self,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, 'MemoryArray']):

        if parent is None:
            raise TypeError('parent should be either AddressMap or Memory Array '
                            f'got {type(parent)}')

        if not isinstance(parent, (AddressMap, MemoryWriteOnlyArray,
                                   MemoryReadOnlyArray, MemoryReadWriteArray)):
            raise TypeError('parent should be either AddressMap or Memory Array '
                            f'got {type(parent)}')

        if not isinstance(parent._callbacks, (NormalCallbackSet, NormalCallbackSetLegacy)):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(address=address,
                         width=width,
                         accesswidth=accesswidth,
                         entries=entries,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    # pylint: enable=too-many-arguments
    @property
    def _callbacks(self) -> Union[NormalCallbackSet, NormalCallbackSetLegacy]:
        # pylint: disable=protected-access
        if self.parent is None:
            raise RuntimeError('Parent must be set')

        if isinstance(self.parent._callbacks, (NormalCallbackSet, NormalCallbackSetLegacy)):
            return self.parent._callbacks

        raise TypeError(f'unhandled parent callback type: {type(self.parent._callbacks)}')

    def _read(self, start_entry: int, number_entries: int) -> List[int]:
        """
        Read from the memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            number_entries: number of entries to read

        Returns: data read from memory

        """

        if not isinstance(start_entry, int):
            raise TypeError(f'start_entry should be an int got {type(start_entry)}')

        if not isinstance(number_entries, int):
            raise TypeError(f'number_entries should be an int got {type(number_entries)}')

        if start_entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries - 1:d} '
                             f'but got {start_entry:d}')

        if number_entries not in range(0, self.entries - start_entry + 1):
            raise ValueError(f'number_entries must be in range 0 to'
                             f' {self.entries - start_entry:d} but got {number_entries:d}')

        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            addr = self.address_lookup(entry=start_entry)
            data_read = \
                read_block_callback(addr=addr,  # type: ignore[call-arg]
                                    width=self.width,  # type: ignore[call-arg]
                                    accesswidth=self.width,  # type: ignore[call-arg]
                                    length=number_entries)  # type: ignore[call-arg]

            if isinstance(self._callbacks, NormalCallbackSet):
                if not isinstance(data_read, List):
                    raise TypeError('The read block callback is expected to return an List')
                return data_read

            if isinstance(self._callbacks, NormalCallbackSetLegacy):
                if not isinstance(data_read, Array):
                    raise TypeError('The read block callback is expected to return an array')
                return data_read.tolist()

            raise RuntimeError(f'There is no usable callback block callback:{read_block_callback}')

        if read_callback is not None:
            # there is not read_block_callback defined so we must used individual read
            data_read = [0 for _ in range(number_entries)]

            for entry in range(number_entries):
                entry_address = self.address_lookup(entry=start_entry+entry)
                # python 3.7 doesn't have the callback defined as protocol so mypy doesn't
                # recognise the arguments in the call back functions
                data_entry = read_callback(addr=entry_address,  # type: ignore[call-arg]
                                           width=self.width,  # type: ignore[call-arg]
                                           accesswidth=self.width)  # type: ignore[call-arg]

                data_read[entry] = data_entry

            return data_read

        raise RuntimeError(f'There is no usable callback, '
                           f'block callback:{read_block_callback}, '
                           f'normal callback:{read_callback}')

    def _read_legacy(self, start_entry: int, number_entries: int) -> Array:
        """
        Read from the memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            number_entries: number of entries to read

        Returns: data read from memory

        """

        if not isinstance(start_entry, int):
            raise TypeError(f'start_entry should be an int got {type(start_entry)}')

        if not isinstance(number_entries, int):
            raise TypeError(f'number_entries should be an int got {type(number_entries)}')

        if start_entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries - 1:d} '
                             f'but got {start_entry:d}')

        if number_entries not in range(0, self.entries - start_entry + 1):
            raise ValueError(f'number_entries must be in range 0 to'
                             f' {self.entries - start_entry:d} but got {number_entries:d}')

        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            addr = self.address_lookup(entry=start_entry)
            data_read = \
                read_block_callback(addr=addr,  # type: ignore[call-arg]
                                    width=self.width,  # type: ignore[call-arg]
                                    accesswidth=self.width,  # type: ignore[call-arg]
                                    length=number_entries)  # type: ignore[call-arg]

            if isinstance(self._callbacks, NormalCallbackSet):
                if not isinstance(data_read, List):
                    raise TypeError('The read block callback is expected to return an List')
                return Array(self.array_typecode, data_read)

            if isinstance(self._callbacks, NormalCallbackSetLegacy):
                if not isinstance(data_read, Array):
                    raise TypeError('The read block callback is expected to return an array')
                return data_read

            raise RuntimeError(f'There is no usable callback block callback:{read_block_callback}')

        if read_callback is not None:
            # there is not read_block_callback defined so we must used individual read
            data_read = Array(self.array_typecode, [0 for _ in range(number_entries)])

            for entry in range(number_entries):
                entry_address = self.address_lookup(entry=start_entry+entry)
                # python 3.7 doesn't have the callback defined as protocol so mypy doesn't
                # recognise the arguments in the call back functions
                data_entry = read_callback(addr=entry_address,  # type: ignore[call-arg]
                                           width=self.width,  # type: ignore[call-arg]
                                           accesswidth=self.width)  # type: ignore[call-arg]

                data_read[entry] = data_entry

            return data_read

        raise RuntimeError(f'There is no usable callback, '
                           f'block callback:{read_block_callback}, '
                           f'normal callback:{read_callback}')

    def get_readable_registers(self, unroll: bool = False) -> \
            Iterator[Union['ReadableRegister', 'ReadableRegisterArray']]:
        """
        generator that produces all the readable_registers of this node

        Args:
            unroll: Whether to unroll child array or not
        """
        def is_readable(item: Union['Reg', 'RegArray']) ->\
                TypeGuard[Union['ReadableRegister', 'ReadableRegisterArray']]:
            # pylint: disable-next=protected-access
            return item._is_readable

        return filter(is_readable, self.get_registers(unroll=unroll))


class MemoryReadOnly(_MemoryReadOnly, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    def read(self, start_entry: int, number_entries: int) -> List[int]:
        """
        Read from the memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            number_entries: number of entries to read

        Returns: data read from memory

        """
        return self._read(start_entry=start_entry, number_entries=number_entries)


class MemoryReadOnlyLegacy(_MemoryReadOnly, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    __slots__: List[str] = []

    def read(self, start_entry: int, number_entries: int) -> Array:
        """
        Read from the memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            number_entries: number of entries to read

        Returns: data read from memory

        """
        return self._read_legacy(start_entry=start_entry, number_entries=number_entries)


class _MemoryWriteOnly(Memory, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments
    def __init__(self,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, 'MemoryArray']):

        if not isinstance(parent, (AddressMap, MemoryWriteOnlyArray,
                                   MemoryReadOnlyArray, MemoryReadWriteArray)):
            raise TypeError('parent should be either AddressMap or Memory Array '
                            f'got {type(parent)}')

        if not isinstance(parent._callbacks, (NormalCallbackSet, NormalCallbackSetLegacy)):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(address=address,
                         width=width,
                         accesswidth=accesswidth,
                         entries=entries,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    # pylint: enable=too-many-arguments
    @property
    def _callbacks(self) -> Union[NormalCallbackSet, NormalCallbackSetLegacy]:
        # pylint: disable=protected-access
        if self.parent is None:
            raise RuntimeError('Parent must be set')

        if isinstance(self.parent._callbacks, (NormalCallbackSet, NormalCallbackSetLegacy)):
            return self.parent._callbacks

        raise TypeError(f'unhandled parent callback type: {type(self.parent._callbacks)}')

    def _write(self, start_entry: int, data: Union[Array, List[int]]) -> None:
        """
        Write data to memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            data: data to write

        Returns: None

        """
        if not isinstance(start_entry, int):
            raise TypeError(f'start_entry should be an int got {type(start_entry)}')

        if start_entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries - 1:d} '
                             f'but got {start_entry:d}')

        if not isinstance(data, (Array, List)):
            raise TypeError(f'data should be an List or array.array got {type(data)}')

        if len(data) not in range(0, self.entries - start_entry + 1):
            raise ValueError(f'data length must be in range 0 to {self.entries - start_entry:d} '
                             f'but got {len(data):d}')

        if self._callbacks.write_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            addr = self.address_lookup(entry=start_entry)
            if isinstance(self._callbacks, NormalCallbackSet):
                if isinstance(data, Array):
                    self._callbacks.write_block_callback(
                        addr=addr,  # type: ignore[call-arg]
                        width=self.width,  # type: ignore[call-arg]
                        accesswidth=self.width,  # type: ignore[call-arg]
                        data=data.tolist())  # type: ignore[call-arg]
                else:
                    self._callbacks.write_block_callback(
                        addr=addr,  # type: ignore[call-arg]
                        width=self.width,  # type: ignore[call-arg]
                        accesswidth=self.width,  # type: ignore[call-arg]
                        data=data)  # type: ignore[call-arg]
            if isinstance(self._callbacks, NormalCallbackSetLegacy):
                if isinstance(data, list):
                    # need to convert the data to an array before calling
                    self._callbacks.write_block_callback(
                        addr=addr,  # type: ignore[call-arg]
                        width=self.width,  # type: ignore[call-arg]
                        accesswidth=self.width,  # type: ignore[call-arg]
                        data=Array(self.array_typecode, data))  # type: ignore[call-arg]
                else:
                    self._callbacks.write_block_callback(
                        addr=addr,  # type: ignore[call-arg]
                        width=self.width,  # type: ignore[call-arg]
                        accesswidth=self.width,  # type: ignore[call-arg]
                        data=data)  # type: ignore[call-arg]

        elif self._callbacks.write_callback is not None:
            # there is not write_block_callback defined so we must used individual write
            for entry_index, entry_data in enumerate(data):
                entry_address = self.address_lookup(entry=start_entry+entry_index)
                # python 3.7 doesn't have the callback defined as protocol so mypy doesn't
                # recognise the arguments in the call back functions
                self._callbacks.write_callback(addr=entry_address,  # type: ignore[call-arg]
                                               width=self.width,  # type: ignore[call-arg]
                                               accesswidth=self.width,  # type: ignore[call-arg]
                                               data=entry_data)  # type: ignore[call-arg]

        else:
            raise RuntimeError('No suitable callback')

    def get_writable_registers(self, unroll: bool = False) -> \
            Iterator[Union['WritableRegister', 'WriteableRegisterArray']]:
        """
        generator that produces all the readable_registers of this node

        Args:
            unroll: Whether to unroll child array or not
        """
        def is_writable(item: Union['Reg', 'RegArray']) -> \
                TypeGuard[Union['WritableRegister', 'WriteableRegisterArray']]:
            # pylint: disable-next=protected-access
            return item._is_writeable

        return filter(is_writable, self.get_registers(unroll=unroll))


class MemoryWriteOnly(_MemoryWriteOnly, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    __slots__: List[str] = []

    def write(self, start_entry: int, data: List[int]) -> None:
        """
        Write data to memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            data: data to write

        Returns: None

        """
        if not isinstance(data, list):
            raise TypeError(f'data should be an List got {type(data)}')
        return self._write(start_entry=start_entry, data=data)


class MemoryWriteOnlyLegacy(_MemoryWriteOnly, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    __slots__: List[str] = []

    def write(self, start_entry: int, data: Array) -> None:
        """
        Write data to memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            data: data to write

        Returns: None

        """
        if not isinstance(data, Array):
            raise TypeError(f'data should be an Array {type(data)}')
        return self._write(start_entry=start_entry, data=data)


class MemoryReadWrite(MemoryReadOnly, MemoryWriteOnly, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []


class MemoryReadWriteLegacy(MemoryReadOnlyLegacy, MemoryWriteOnlyLegacy, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []


class MemoryReadOnlyArray(NodeArray, ABC):
    """
    base class for a array of read only memories
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions)


class MemoryWriteOnlyArray(NodeArray, ABC):
    """
    base class for a array of write only memories
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions)


class MemoryReadWriteArray(MemoryReadOnlyArray, MemoryWriteOnlyArray, ABC):
    """
    base class for a array of read and write memories
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        if not isinstance(parent, AddressMap):
            raise TypeError(f'parent should be either AddressMap got {type(parent)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions)


ReadableMemory = Union[MemoryReadOnly, MemoryReadWrite]
WritableMemory = Union[MemoryWriteOnly, MemoryReadWrite]
ReadableMemoryLegacy = Union[MemoryReadOnlyLegacy, MemoryReadWriteLegacy]
WritableMemoryLegacy = Union[MemoryWriteOnlyLegacy, MemoryReadWriteLegacy]
MemoryArray = Union[MemoryReadOnlyArray, MemoryWriteOnlyArray, MemoryReadWriteArray]
