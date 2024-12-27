"""
Tests for the array indexing in the base library
"""

import unittest
from typing import Optional, Union, cast
from collections.abc import Iterator
from abc import ABC, abstractmethod
from unittest.mock import patch
from array import array as Array

# pylint: disable-next=unused-wildcard-import, wildcard-import
from peakrdl_python.lib import *

from .simple_components import ReadWriteRegisterArrayToTest, ReadOnlyRegisterArrayToTest, \
    WriteOnlyRegisterArrayToTest, CallBackTestWrapper

# pylint: disable=logging-not-lazy,logging-fstring-interpolation

class ArrayBase(CallBackTestWrapper, ABC):
    """
    Base of the Array indexing tests
    """
    # pylint: disable=duplicate-code
    @property
    @abstractmethod
    def RegisterArrayType(self):  # pylint: disable=invalid-name
        """
        type of register array to test
        """

    @property
    @abstractmethod
    def dimensions(self) -> tuple[int, ...]:
        """
        Array dimensions
        """

    @property
    @abstractmethod
    def base_address(self) -> int:
        """
        Array address
        """

    @property
    @abstractmethod
    def stride(self) -> int:
        """
        Array address stride
        """

    @property
    def dut(self):
        """
        Register Array under test
        """
        return self.__dut_warpper.dut

    @abstractmethod
    def calculate_address(self, indices: tuple[int, ...]) -> int:
        """
        address based on array index
        """

    def setUp(self) -> None:

        class DUTWrapper(AddressMap):
            """
            Address map to to wrap the register array being tested
            """

            # pylint: disable=too-many-arguments,duplicate-code
            def __init__(self, *,
                         callbacks: Optional[CallbackSet],
                         address: int,
                         logger_handle: str,
                         inst_name: str,
                         dut_stride : int,
                         dut_dimensions : tuple[int, ...],
                         RegisterArrayType):

                super().__init__(callbacks=callbacks, address=address, logger_handle=logger_handle,
                                 inst_name=inst_name, parent=None )

                self.__dut = RegisterArrayType(logger_handle='dut',
                                               inst_name='dut',
                                               parent=self,
                                               address=address,
                                               accesswidth=32,
                                               width=32,
                                               stride=dut_stride,
                                               dimensions=dut_dimensions)

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

            # pylint: enable=duplicate-code

            @property
            def dut(self):
                """
                Register Array under Test
                """
                return self.__dut

            @property
            def size(self) -> int:
                return self.dut.size

        super().setUp()
        self.__dut_warpper = DUTWrapper(callbacks=self.callbacks, address=self.base_address,
                                        logger_handle='dut_wrapper', inst_name='dut_wrapper',
                                        dut_stride=self.stride, dut_dimensions=self.dimensions,
                                        RegisterArrayType=self.RegisterArrayType)


class Test1DArrayReadWrite(ArrayBase):
    """
    Test for 1D arrays
    """
    @property
    def RegisterArrayType(self):
        """
        type of register array to test
        """
        return ReadWriteRegisterArrayToTest

    @property
    def dut(self) -> ReadWriteRegisterArrayToTest:
        """
        type of register array to test
        """
        return cast(ReadWriteRegisterArrayToTest, super().dut)

    # pylint: disable=duplicate-code
    @property
    def dimensions(self) -> tuple[int, ...]:
        return (10,)

    @property
    def stride(self) -> int:
        return 4

    @property
    def base_address(self) -> int:
        return 0

    def calculate_address(self, indices: tuple[int, ...]) -> int:
        return (indices[0] * self.stride) + self.base_address

    # pylint: enable=duplicate-code

    def test_block_context_manager(self):
        """
        test the context manager that will perform a single block read, modify write with
        optional read-verify
        """

        # try a standard operation
        with patch.object(self.callbacks, 'read_block_callback',
                          return_value=[0 for x in range(10)]) as read_patch, \
                patch.object(self.callbacks, 'write_block_callback') as write_patch:

            follow_along_array = [0 for x in range(10)]
            with self.dut.single_read_modify_write() as dut_context:
                self.assertEqual(dut_context[2].read(), follow_along_array[2])
                dut_context[2].write(4)
                follow_along_array[2] = 4
                self.assertEqual(dut_context[2].read(), follow_along_array[2])
                dut_context[3].write(5)
                follow_along_array[3] = 5
                self.assertEqual(dut_context[3].read(), follow_along_array[3])
                dut_context[2].write(6)
                follow_along_array[2] = 6
                self.assertEqual(dut_context[2].read(), follow_along_array[2])
                dut_context[4].field.write(True)
                follow_along_array[4] = 1 # filed is in bit 0

            read_patch.assert_called_once_with(addr=0, width=32, accesswidth=32, length=10)
            write_patch.assert_called_once_with(addr=0, width=32,
                                                accesswidth=32, data=follow_along_array)

        # try with write-back skip
        with patch.object(self.callbacks, 'read_block_callback',
                          return_value=[0 for x in range(10)]) as read_patch, \
                patch.object(self.callbacks, 'write_block_callback') as write_patch:
            with self.dut.single_read_modify_write(skip_write=True) as dut_context:
                dut_context[2].write(4)

            read_patch.assert_called_once_with(addr=0, width=32, accesswidth=32, length=10)
            write_patch.assert_not_called()

        # try with a read-back verify error, that is expected to fail
        with self.assertRaises(RegisterWriteVerifyError):
            with patch.object(self.callbacks, 'read_block_callback',
                              side_effect=self.read_block_addr_space) as read_patch, \
                    patch.object(self.callbacks, 'write_block_callback') as write_patch:

                with self.dut.single_read_modify_write(verify=True) as dut_context:
                    dut_context[2].write(4)

    def test_blockless_context_manager(self):
        """
        test the context manager that will perform a set of read operation,
        modify write operations with optional read-verify
        """


class Test1DArrayReadOnly(ArrayBase):
    """
    Test for 1D arrays
    """
    @property
    def RegisterArrayType(self):
        """
        type of register array to test
        """
        return ReadOnlyRegisterArrayToTest

    @property
    def dut(self) -> ReadOnlyRegisterArrayToTest:
        """
        type of register array to test
        """
        return cast(ReadOnlyRegisterArrayToTest, super().dut)

    # pylint: disable=duplicate-code
    @property
    def dimensions(self) -> tuple[int, ...]:
        return (10,)

    @property
    def stride(self) -> int:
        return 4

    @property
    def base_address(self) -> int:
        return 0

    def calculate_address(self, indices: tuple[int, ...]) -> int:
        return (indices[0] * self.stride) + self.base_address

    # pylint: enable=duplicate-code

    def test_block_context_manager(self):
        """
        test the context manager that will perform a single block read, modify write with
        optional read-verify
        """

        # try a standard operation
        with patch.object(self.callbacks, 'read_block_callback',
                          return_value=[x+9 for x in range(10)]) as read_patch, \
                patch.object(self.callbacks, 'write_block_callback') as write_patch:

            with self.dut.single_read() as dut_context:
                for idx, item in enumerate(dut_context):
                    self.assertEqual(item.read(), idx+9)

            write_patch.assert_not_called()
            read_patch.assert_called_once_with(addr=0, width=32, accesswidth=32, length=10)

    def test_blockless_context_manager(self):
        """
        test the context manager that will perform a set of read operation,
        modify write operations with optional read-verify
        """


class Test1DArrayWriteOnly(ArrayBase):
    """
    Test for 1D arrays
    """
    @property
    def RegisterArrayType(self):
        """
        type of register array to test
        """
        return WriteOnlyRegisterArrayToTest

    @property
    def dut(self) -> WriteOnlyRegisterArrayToTest:
        """
        type of register array to test
        """
        return cast(WriteOnlyRegisterArrayToTest, super().dut)

    # pylint: disable=duplicate-code
    @property
    def dimensions(self) -> tuple[int, ...]:
        return (10,)

    @property
    def stride(self) -> int:
        return 4

    @property
    def base_address(self) -> int:
        return 0

    def calculate_address(self, indices: tuple[int, ...]) -> int:
        return (indices[0] * self.stride) + self.base_address

    # pylint: enable=duplicate-code

    def test_block_context_manager(self):
        """
        test the context manager that will perform a single block read, modify write with
        optional read-verify
        """

        # try a standard operation
        with patch.object(self.callbacks, 'read_block_callback',
                          return_value=Array('L', [0 for x in range(10)])) as read_patch, \
                patch.object(self.callbacks, 'write_block_callback') as write_patch:

            follow_along_array = [0 for x in range(10)]
            with self.dut.single_write() as dut_context:
                for idx, item in enumerate(dut_context):
                    item.write(idx+29)
                    follow_along_array[idx] = idx+29


            read_patch.assert_not_called()
            write_patch.assert_called_once_with(addr=0, width=32,
                                                accesswidth=32, data=follow_along_array)

    def test_blockless_context_manager(self):
        """
        test the context manager that will perform a set of read operation,
        modify write operations with optional read-verify
        """


if __name__ == '__main__':
    unittest.main()
