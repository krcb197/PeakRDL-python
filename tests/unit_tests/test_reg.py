"""
Test for basic register reading
"""
import unittest
from typing import Optional, cast, Union
from collections.abc import Iterator
from abc import ABC, abstractmethod
from unittest.mock import patch

# pylint: disable-next=unused-wildcard-import,wildcard-import
from peakrdl_python.lib import *
from peakrdl_python.lib.utility_functions import legal_register_width

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
    def reg_type(self) -> type[Union[ReadOnlyRegisterToTest,
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
            def __init__(self, *,
                         callbacks: Optional[CallbackSet],
                         address: int,
                         logger_handle: str,
                         inst_name: str,
                         reg_type: type[Union[ReadOnlyRegisterToTest,
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
                    Iterator[Union[Memory, tuple[Memory, ...]]]:
                raise NotImplementedError('Not implemented in the testing')

            def get_sections(self, unroll: bool = False) -> \
                    Iterator[Union[Union[AddressMap, RegFile],
                                   tuple[Union[AddressMap, RegFile], ...]]]:
                raise NotImplementedError('Not implemented in the testing')

            def get_registers(self, unroll: bool = False) -> \
                    Iterator[Union[Reg, RegArray]]:
                """
                generator that produces all the readable_registers of this node
                """
                raise NotImplementedError('Not implemented in the testing')

            @property
            def systemrdl_python_child_name_map(self) -> dict[str, str]:

                return {
                    'dut': 'dut'
                }

            @property
            def dut(self) -> Reg:
                """
                Register under tests
                """
                return self.__dut

            @property
            def size(self) -> int:
                return self.dut.size

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
    def reg_type(self) -> type[ReadOnlyRegisterToTest]:
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
    def reg_type(self) -> type[WriteOnlyRegisterToTest]:
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
    def reg_type(self) -> type[ReadWriteRegisterToTest]:
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

    def test_context_manager_read_modify_write_check_writeback(self) -> None:
        """
        Check the write back has occurred, this happens by default even if nothing has changed in
        the register
        """

        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.dut.single_read_modify_write() as reg:
                _ = reg.field.read()
                _ = reg.field.read()

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth, data=0)

        # check the `skip_write` works as expected, this will however raise an deprecation warning
        # and the feature will be removed at some point in the future
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.dut.single_read_modify_write(skip_write=True) as reg:
                _ = reg.field.read()
                _ = reg.field.read()

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

        # check that a write within the `skip_write` works still does not result in a write
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.dut.single_read_modify_write(skip_write=True) as reg:
                self.assertEqual(reg.field.read(), False)
                self.assertEqual(reg.field.read(), False)
                reg.field.write(True)
                self.assertEqual(reg.field.read(), True)

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

        # attempting to use the `single_read` inside the `single_read_modify_write` context
        # should cause an exception
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.dut.single_read_modify_write() as reg:
                _ = reg.field.read()
                with self.assertRaises(RuntimeError):
                    with reg.single_read() as alt_reg:
                        _ = alt_reg.field.read()

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_called_once_with(addr=0,
                                                width=self.dut.width,
                                                accesswidth=self.dut.accesswidth, data=0)

        # check the context manager cleans itself up properly even if an exception occurs within
        # the context
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:
            with self.assertRaises(TypeError):
                with self.dut.single_read_modify_write() as reg:
                    _ = reg.field.read()
                    reg.field.write(1.1)

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            read_patch.reset_mock()
            write_patch.assert_not_called()

            # make sure it has not been left in a bad internal state
            _ = reg.field.read()
            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)

    def test_read_fields(self) -> None:
        """
        Check the read fields methods reads the fields
        """
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            result = self.dut.read_fields()

            self.assertDictEqual(result, {'field': False})

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

    def test_context_manager_read(self) -> None:
        """
        Check the write back has occurred, this happens by default even if nothing has changed in
        the register
        """

        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.dut.single_read() as reg:
                _ = reg.field.read()
                _ = reg.field.read()

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

        # attempting a write in the single read context manager should raise an exception
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.dut.single_read() as reg:
                _ = reg.field.read()
                with self.assertRaises(RuntimeError):
                    reg.field.write(True)

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

        # attempting to use the `single_read_modify_write` inside the `single_read` context
        # should cause an exception
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.dut.single_read() as reg:
                _ = reg.field.read()
                with self.assertRaises(RuntimeError):
                    with reg.single_read_modify_write() as alt_reg:
                        _ = alt_reg.field.read()

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            write_patch.assert_not_called()

        # an exception within the `single_read` context must not leave the register in a bad
        # state
        with patch.object(self.callbacks, 'read_callback',
                          side_effect=self.read_addr_space) as read_patch, \
                patch.object(self.callbacks, 'write_callback',
                             side_effect=self.write_addr_space) as write_patch:

            with self.assertRaises(ZeroDivisionError):
                with self.dut.single_read() as reg:
                    _ = reg.field.read()
                    _ = reg.field.read()
                    # the following line is deliberately intended to cause an exception
                    _ = 10 / 0

            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            read_patch.reset_mock()
            write_patch.assert_not_called()

            self.dut.read()
            read_patch.assert_called_once_with(addr=0,
                                               width=self.dut.width,
                                               accesswidth=self.dut.accesswidth)
            read_patch.reset_mock()

            self.dut.field.write(True)
            write_patch.assert_called_once_with(addr=0,
                                                width=self.dut.width,
                                                accesswidth=self.dut.accesswidth, data=1)


class TestRegWidthUtility(unittest.TestCase):
    """
    Test for the register width calculations
    """

    def test_legal_reg_width(self):
        """
        Test the register widths
        """
        self.assertFalse(legal_register_width(-1))
        self.assertFalse(legal_register_width(0))
        self.assertFalse(legal_register_width(4))
        for width_power in range(3, 20):
            reg_width = 1 << width_power
            self.assertTrue(legal_register_width(reg_width))
            self.assertFalse(legal_register_width(reg_width + 1))
            self.assertFalse(legal_register_width(reg_width - 1))
