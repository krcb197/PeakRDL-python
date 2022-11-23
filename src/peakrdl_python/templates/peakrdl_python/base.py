"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of base classes used by the autogenerated code
"""
from __future__ import annotations
import logging
from typing import List, Optional
from abc import ABC

from .callbacks import CallbackSet


class Base(ABC):
    """
    base class of for all types

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    #pylint: disable=too-few-public-methods
    __slots__ : List[str] = ['__logger', '__inst_name', '__parent']

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
        name of the instance in the parent
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
        The full hierarchical name of the instance
        """
        if self.parent is not None:
            return self.parent.full_inst_name + "." + self.inst_name

        return self.inst_name


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
    def _callbacks(self):
        return self.__callbacks


class AddressMap(Node, ABC):
    """
    base class of address map wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ : List[str] = []


class RegFile(Node, ABC):
    """
    base class of register file wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ : List[str] = []


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
