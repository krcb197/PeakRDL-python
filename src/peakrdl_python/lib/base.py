"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of base classes used by the autogenerated code
"""
from __future__ import annotations
import logging
from typing import Dict, List, Optional, Tuple, Union, cast, Iterator, TYPE_CHECKING
from abc import ABC, abstractmethod

from .callbacks import CallbackSet

if TYPE_CHECKING:
    from .memory import Memory

class Base(ABC):
    """
    base class of for all types
    """
    __slots__: List[str] = ['__logger', '__inst_name', '__parent']

    def __init__(self, logger_handle: str, inst_name: str, parent: Optional[Base]):
        self.__logger = logging.getLogger(logger_handle)
        self._logger.debug('creating instance of %s', self.__class__)

        self.__inst_name = inst_name
        self.__parent = parent

    @property
    def _logger(self) -> logging.Logger:
        return self.__logger

    @property
    def inst_name(self) -> str:
        """
        systemRDL name of the instance in the parent
        """
        return self.__inst_name

    @property
    def parent(self) -> Optional[Base]:
        """
        parent of the node or field, or None if it has no parent
        """
        return self.__parent

    @property
    def full_inst_name(self) -> str:
        """
        The full hierarchical system RDLname of the instance
        """
        if self.parent is not None:
            return self.parent.full_inst_name + "." + self.inst_name

        return self.inst_name


class BaseArray(Base, ABC):
    """
    base class of for all array types
    """

    # pylint: disable=too-few-public-methods
    __slots__: List[str] = ['__elements']

    def __init__(self, logger_handle: str, inst_name: str, parent: Optional[Base],
                 elements: Tuple[Base, ...]):
        super().__init__(logger_handle=logger_handle, inst_name=inst_name, parent=parent)

        if not isinstance(elements, tuple):
            raise TypeError(f'expected elements to be tuple, got {type(elements)}')

        self.__elements = elements

    def __getitem__(self, item: Union[slice, int]) -> Union[Base, Tuple[Base, ...]]:
        return self.__elements[item]

    def __len__(self) -> int:
        return len(self.__elements)

    def __iter__(self) -> Iterator[Base]:
        return self.__elements.__iter__()


class Node(Base, ABC):
    """
    base class of for all types with an address i.e. not fields

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = ['__address', '__callbacks']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional[Base]):
        super().__init__(logger_handle=logger_handle, inst_name=inst_name, parent=parent)

        self.__address = address
        self.__callbacks = callbacks

    @property
    def address(self) -> int:
        """
        address of the node
        """
        return self.__address

    @property
    def _callbacks(self) -> CallbackSet:
        return self.__callbacks

    @property
    @abstractmethod
    def systemrdl_python_child_name_map(self) -> Dict[str, str]:
        """
        In some cases systemRDL names need to be converted make them python safe, this dictionary
        is used to map the original systemRDL names to the names of the python attributes of this
        class

        Returns: dictionary whose key is the systemRDL names and value it the property name
        """

    def get_child_by_system_rdl_name(self, name: str) -> Base:
        """
        returns a child node by its systemRDL name

        Args:
            name: name of the node in the systemRDL

        Returns: Node

        """
        return getattr(self, self.systemrdl_python_child_name_map[name])


class AddressMap(Node, ABC):
    """
    base class of address map wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional['AddressMap']):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    @abstractmethod
    def get_sections(self, unroll: bool = False) -> \
            Iterator[Union[Union['AddressMap', RegFile],
                           Tuple[Union['AddressMap', RegFile], ...]]]:
        """
        generator that produces all the AddressMap and RegFile children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """

    @abstractmethod
    def get_memories(self, unroll:bool=False) -> Iterator[Union['Memory', Tuple['Memory', ...]]]:
        """
        generator that produces all the Memory children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """


class AddressMapArray(BaseArray, ABC):
    """
    base class for a array of address maps
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 elements: Tuple[AddressMap, ...]):

        for element in elements:
            if not isinstance(element, AddressMap):
                raise TypeError(
                    f'All Elements should be of type AddressMap, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item: Union[int, slice]) -> Union[AddressMap, Tuple[AddressMap, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[AddressMap, Tuple[AddressMap, ...]], super().__getitem__(item))


class RegFile(Node, ABC):
    """
    base class of register file wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, 'RegFile']):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    @abstractmethod
    def get_sections(self, unroll:bool=False) -> Iterator[Union['RegFile', Tuple['RegFile', ...]]]:
        """
        generator that produces all the RegFile children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """


class RegFileArray(BaseArray, ABC):
    """
    base class for a array of register files
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[AddressMap, RegFile],
                 elements: Tuple[RegFile, ...]):

        for element in elements:
            if not isinstance(element, RegFile):
                raise TypeError(
                    f'All Elements should be of type RegFile, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item: Union[int, slice]) -> Union[RegFile, Tuple[RegFile, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[RegFile, Tuple[RegFile, ...]], super().__getitem__(item))


def swap_msb_lsb_ordering(width: int, value: int) -> int:
    """
    swaps the msb/lsb on a integer

    Returns:
        swapped value
    """
    value_to_return = 0
    for bit_positions in zip(range(0, width), range(width-1, -1, -1)):
        bit_value = (value >> bit_positions[0]) & 0x1
        value_to_return |= bit_value << bit_positions[1]

    return value_to_return

def get_array_typecode(width: int) -> str:
    """
        python array typecode

        Args:
            width: in tbits

        Returns:
            string to pass into the array generator

        """
    if width == 32:
        return 'L'

    if width == 64:
        return 'Q'

    if width == 16:
        return 'I'

    if width == 8:
        return 'B'

    raise ValueError(f'unhandled width {width:d}')