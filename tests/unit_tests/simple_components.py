"""
Components to use in unit tests
"""
import unittest
from unittest.mock import NonCallableMagicMock
from typing import List, Iterator, Dict, Type, Any, Union
from abc import ABC
import logging
from array import array as Array

# pylint: disable-next=unused-wildcard-import, wildcard-import
from peakrdl_python.lib import *

# pylint: disable=logging-not-lazy,logging-fstring-interpolation

class ReadOnlyRegisterToTest(RegReadOnly):
    """
    Class to represent a register in the register model
    """
    __slots__: List[str] = ['__field']

    class FieldToTest(FieldReadOnly):
        """
        Class to represent a register field in the register model
        """
        __slots__: List[str] = []

    # pylint: disable=duplicate-code,too-many-arguments
    def __init__(self,
                 address: int,
                 accesswidth:int,
                 width:int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):
        super().__init__(address=address,
                         accesswidth=accesswidth,
                         width=width,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__field = self.FieldToTest(
            parent_register=self,
            size_props=FieldSizeProps(
                width=1,
                lsb=0,
                msb=0,
                low=0,
                high=0),
            misc_props=FieldMiscProps(
                default=None,
                is_volatile=False),
            logger_handle=logger_handle + '.field',
            inst_name='field')

    @property
    def readable_fields(self) -> Iterator[FieldReadOnly]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.field

    # build the properties for the fields
    @property
    def field(self) -> FieldToTest:
        """
        Property to access field of the register
        """
        return self.__field

    @property
    def systemrdl_python_child_name_map(self) -> Dict[str, str]:
        """
        In some cases systemRDL names need to be converted make them python safe, this dictionary
        is used to map the original systemRDL names to the names of the python attributes of this
        class

        Returns: dictionary whose key is the systemRDL names and value it the property name
        """
        return {
            'field': 'field',
        }

class WriteOnlyRegisterToTest(RegWriteOnly):
    """
    Class to represent a register in the register model
    """
    __slots__: List[str] = ['__field']

    # pylint: disable=duplicate-code,too-many-arguments
    class FieldToTest(FieldWriteOnly):
        """
        Class to represent a register field in the register model
        """
        __slots__: List[str] = []

    def __init__(self,
                 address: int,
                 accesswidth: int,
                 width: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):
        super().__init__(address=address,
                         accesswidth=accesswidth,
                         width=width,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__field = self.FieldToTest(
            parent_register=self,
            size_props=FieldSizeProps(
                width=1,
                lsb=0,
                msb=0,
                low=0,
                high=0),
            misc_props=FieldMiscProps(
                default=None,
                is_volatile=False),
            logger_handle=logger_handle + '.field',
            inst_name='field')

    @property
    def writable_fields(self) -> Iterator[FieldWriteOnly]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.field

    def write_fields(self, **kwargs: Any) -> None:
        raise NotImplementedError('Not Implemented for the purpose of testing')

    # build the properties for the fields
    @property
    def field(self) -> FieldToTest:
        """
        Property to access field of the register
        """
        return self.__field

    @property
    def systemrdl_python_child_name_map(self) -> Dict[str, str]:
        """
        In some cases systemRDL names need to be converted make them python safe, this dictionary
        is used to map the original systemRDL names to the names of the python attributes of this
        class

        Returns: dictionary whose key is the systemRDL names and value it the property name
        """
        return {
            'field': 'field',
        }

class ReadWriteRegisterToTest(RegReadWrite):
    """
    Class to represent a register in the register model
    """
    __slots__: List[str] = ['__field']

    # pylint: disable=duplicate-code,too-many-arguments
    class FieldToTest(FieldReadWrite):
        """
        Class to represent a register field in the register model
        """
        __slots__: List[str] = []

    def __init__(self,
                 address: int,
                 accesswidth: int,
                 width: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):
        super().__init__(address=address,
                         accesswidth=accesswidth,
                         width=width,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__field = self.FieldToTest(
            parent_register=self,
            size_props=FieldSizeProps(
                width=1,
                lsb=0,
                msb=0,
                low=0,
                high=0),
            misc_props=FieldMiscProps(
                default=None,
                is_volatile=False),
            logger_handle=logger_handle + '.field',
            inst_name='field')

    @property
    def readable_fields(self) -> Iterator[FieldReadOnly]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.field

    @property
    def writable_fields(self) -> Iterator[Union['FieldWriteOnly', 'FieldReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.field

    # build the properties for the fields
    @property
    def field(self) -> FieldToTest:
        """
        Property to access field of the register
        """
        return self.__field

    def write_fields(self,  **kwargs: Any) -> None:
        raise NotImplementedError('Not implemented for the purpose of tests')

    @property
    def systemrdl_python_child_name_map(self) -> Dict[str, str]:
        """
        In some cases systemRDL names need to be converted make them python safe, this dictionary
        is used to map the original systemRDL names to the names of the python attributes of this
        class

        Returns: dictionary whose key is the systemRDL names and value it the property name
        """
        return {
            'field': 'field',
        }

class ReadOnlyRegisterArrayToTest(RegReadOnlyArray):
    """
    Class to represent a register array in the register model
    """
    __slots__: List[str] = []

    @property
    def _element_datatype(self) -> Type[Node]:
        return ReadOnlyRegisterToTest

class WriteOnlyRegisterArrayToTest(RegWriteOnlyArray):
    """
    Class to represent a register array in the register model
    """
    __slots__: List[str] = []

    @property
    def _element_datatype(self) -> Type[Node]:
        return WriteOnlyRegisterToTest

class ReadWriteRegisterArrayToTest(RegReadWriteArray):
    """
    Class to represent a register array in the register model
    """
    __slots__: List[str] = []

    @property
    def _element_datatype(self) -> Type[Node]:
        return ReadWriteRegisterToTest


class CallBackTestWrapper(unittest.TestCase, ABC):
    """
    Class be used in test cases to provide mockable callbacks
    """

    # dummy functions to demonstrate the class
    def read_addr_space(self, addr: int, width: int, accesswidth: int) -> int:
        """
        Callback to simulate the operation of the package, everytime the read is called, it will
        request the user input the value to be read back.

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits

        Returns:
            value inputted by the used
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        return 0

    def write_addr_space(self, addr: int, width: int, accesswidth: int, data: int) -> None:
        """
        Callback to simulate the operation of the package, everytime the read is called, it will
        request the user input the value to be read back.

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits
            data: value to be written to the register

        Returns:
            None
        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        assert isinstance(data, int)
        self.logger.info(f'write data:{data:X} to address:0x{addr:X}')

    def read_block_addr_space(self, addr: int, width: int, accesswidth: int, length: int) -> List:
        """
        Callback to simulate the operation of the package

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits
            length: number of width entries

        Returns:

        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        assert isinstance(length, int)

        return [0 for x in range(length)]

    def write_block_addr_space(self, addr: int,
                               width: int, accesswidth: int, data: List[int]) -> None:
        """
        Callback to simulate the operation of the package

        Args:
            addr: Address to write to
            width: Width of the register in bits
            accesswidth: Minimum access width of the register in bits
            data: value to be written to the register

        Returns:

        """
        assert isinstance(addr, int)
        assert isinstance(width, int)
        assert isinstance(accesswidth, int)
        assert isinstance(data, List)

    def setUp(self) -> None:
        # the callbacks need to a faked magic mock so that the methods can be patched in tests
        mocked_callback_set = NonCallableMagicMock(spec=NormalCallbackSet)
        attrs = {'read_callback': None,
                 'write_callback': None,
                 'read_block_callback': None,
                 'write_block_callback': None}
        mocked_callback_set.configure_mock(**attrs)
        self.callbacks = mocked_callback_set
        self.logger = logging.Logger('test case')
