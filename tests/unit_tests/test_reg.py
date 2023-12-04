"""
Test for basic register reading
"""
from typing import Tuple, Optional, Iterator, Union, Dict, Type, cast
from abc import ABC, abstractmethod
from unittest.mock import patch

# pylint: disable-next=unused-wildcard-import,wildcard-import
from peakrdl_python.lib import *

from .simple_components import ReadOnlyRegisterToTest, WriteOnlyRegisterToTest, \
    ReadWriteRegisterToTest, CallBackTestWrapper

# pylint: disable=logging-not-lazy,logging-fstring-interpolation

class RegTestBase(CallBackTestWrapper, ABC):
    """
    Base test for the register tests, this will allow this module to extend to checking
    Read/WriteOnly/ReadWrite
    """

    @property
    @abstractmethod
    def address(self) -> int:
        """
        Register Address
        """

    @property
    @abstractmethod
    def reg_type(self) -> Type[Union[ReadOnlyRegisterToTest,
                               WriteOnlyRegisterToTest,
                               ReadWriteRegisterToTest]]:
        """
        Register Class to test
        """

    def setUp(self) -> None:

        class DUTWrapper(AddressMap):
            """
            Address map to to wrap the register being tested
            """

            # pylint: disable=duplicate-code
            def __init__(self,
                         callbacks: Optional[CallbackSet],
                         address: int,
                         logger_handle: str,
                         inst_name: str,
                         reg_type: Type[Union[ReadOnlyRegisterToTest,
                                              WriteOnlyRegisterToTest,
                                              ReadWriteRegisterToTest]]):

                super().__init__(callbacks=callbacks, address=address, logger_handle=logger_handle,
                                 inst_name=inst_name, parent=None)

                self.__dut = reg_type(logger_handle='dut',
                                      inst_name='dut',
                                      parent=self,
                                      width=32,
                                      accesswidth=32,
                                      address=address)

            def get_memories(self, unroll: bool = False) -> \
                    Iterator[Union[Memory, Tuple[Memory, ...]]]:
                raise NotImplementedError('Not implemented in the testing')

            def get_sections(self, unroll: bool = False) -> \
                    Iterator[Union[Union[AddressMap, RegFile],
                                   Tuple[Union[AddressMap, RegFile], ...]]]:
                raise NotImplementedError('Not implemented in the testing')

            def get_registers(self, unroll: bool = False) -> \
                    Iterator[Union[Reg, RegArray]]:
                """
                generator that produces all the readable_registers of this node
                """
                raise NotImplementedError('Not implemented in the testing')

            @property
            def systemrdl_python_child_name_map(self) -> Dict[str, str]:

                return {
                    'dut': 'dut'
                }

            @property
            def dut(self) -> Reg:
                """
                Register under tests
                """
                return self.__dut

        super().setUp()
        self.dut_wrapper = DUTWrapper(callbacks=self.callbacks, address=self.address,
                                      logger_handle='dut_wrapper', inst_name='dut_wrapper',
                                      reg_type=self.reg_type)

class TestReadOnly(RegTestBase):
    """
    Test for read only register
    """

    @property
    def address(self) -> int:
        """
        Register Address
        """
        return 0

    @property
    def reg_type(self) -> Type[ReadOnlyRegisterToTest]:
        """
        Register Class to test
        """
        return ReadOnlyRegisterToTest

    @property
    def dut(self) -> ReadOnlyRegisterToTest:
        """
        Register under test
        """
        return cast(ReadOnlyRegisterToTest, self.dut_wrapper.dut)


    def test_register_read(self) -> None:
        """
        Test register read
        """
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            _ = self.dut.read()
            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            _ = self.dut.field.read()
            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

    def test_context_manager_read(self) -> None:
        """
        Test register context manager read
        """
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            # calling it twice should result in two calls
            _ = self.dut.field.read()
            _ = self.dut.field.read()

            self.assertEqual(read_patch.call_count, 2)
            read_patch.reset_mock()

            # calling it from within the single read contect manager should cause only one
            # read to occur
            with self.dut.single_read():
                _ = self.dut.field.read()
                _ = self.dut.field.read()

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)

            write_patch.assert_not_called()

class TestWrite(RegTestBase):
    """
    Test for write only register
    """

    @property
    def address(self) -> int:
        """
        Register Address
        """
        return 0

    @property
    def reg_type(self) -> Type[WriteOnlyRegisterToTest]:
        """
        Register Class to test
        """
        return WriteOnlyRegisterToTest

    @property
    def dut(self) -> WriteOnlyRegisterToTest:
        """
        Register under test
        """
        return cast(WriteOnlyRegisterToTest, self.dut_wrapper.dut)

    def test_register_write(self) -> None:
        """
        Test register write
        """
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            self.dut.write(10)
            write_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth, data=10)
            read_patch.assert_not_called()

        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            self.dut.field.write(True)
            write_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth, data=1)
            read_patch.assert_not_called()

class TestReadWrite(RegTestBase):
    """
    Test for read/write register
    """

    @property
    def address(self) -> int:
        """
        Register Address
        """
        return 0

    @property
    def reg_type(self) -> Type[ReadWriteRegisterToTest]:
        """
        Register Class to test
        """
        return ReadWriteRegisterToTest

    @property
    def dut(self) -> ReadWriteRegisterToTest:
        """
        Register under test
        """
        return cast(ReadWriteRegisterToTest, self.dut_wrapper.dut)

    def test_register_write(self) -> None:
        """
        Test register write
        """

        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            self.dut.write(10)
            write_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth, data=10)
            read_patch.assert_not_called()

        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            self.dut.field.write(True)
            write_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth, data=1)
            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)

    def test_register_read(self) -> None:
        """
        Test register read
        """
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            _ = self.dut.read()
            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            _ = self.dut.field.read()
            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()
