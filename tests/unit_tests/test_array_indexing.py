"""
Tests for the array indexing in the base library
"""

import unittest
from typing import Tuple, Optional, Iterator, Union, Dict
from abc import ABC, abstractmethod
from itertools import product

# pylint: disable-next=unused-wildcard-import, wildcard-import
from peakrdl_python.lib import *

from .simple_components import ReadOnlyRegisterArrayToTest, CallBackTestWrapper

# pylint: disable=logging-not-lazy,logging-fstring-interpolation

class ArrayBase(CallBackTestWrapper, ABC):
    """
    Base of the Array indexing tests
    """

    @property
    @abstractmethod
    def dimensions(self) -> Tuple[int, ...]:
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
    def dut(self) -> ReadOnlyRegisterArrayToTest:
        """
        Register Array under test
        """
        return self.__dut_warpper.dut

    @abstractmethod
    def calculate_address(self, indices: Tuple[int, ...]) -> int:
        """
        address based on array index
        """


    def setUp(self) -> None:

        class DUTWrapper(AddressMap):
            """
            Address map to to wrap the register array being tested
            """

            # pylint: disable=too-many-arguments,duplicate-code
            def __init__(self,
                         callbacks: Optional[CallbackSet],
                         address: int,
                         logger_handle: str,
                         inst_name: str,
                         dut_stride : int,
                         dut_dimensions : Tuple[int, ...]):


                super().__init__(callbacks=callbacks, address=address, logger_handle=logger_handle,
                                 inst_name=inst_name, parent=None )

                self.__dut = ReadOnlyRegisterArrayToTest(logger_handle='dut',
                                                         inst_name='dut',
                                                         parent=self,
                                                         address=address,
                                                         width=32,
                                                         accesswidth=32,
                                                         stride=dut_stride,
                                                         dimensions=dut_dimensions)

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
                generator that produces all the registers of this node
                """
                raise NotImplementedError('Not implemented in the testing')

            @property
            def systemrdl_python_child_name_map(self) -> Dict[str, str]:

                return {
                    'dut': 'dut'
                }

            # pylint: enable=duplicate-code

            @property
            def dut(self) -> ReadOnlyRegisterArrayToTest:
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
                                        dut_stride=self.stride, dut_dimensions=self.dimensions)


class Test1DArray(ArrayBase):
    """
    Test for 1D arrays
    """


    @property
    def dimensions(self) -> Tuple[int, ...]:
        return (10,)

    @property
    def stride(self) -> int:
        return 4

    @property
    def base_address(self) -> int:
        return 0

    def calculate_address(self, indices: Tuple[int, ...]) -> int:
        return (indices[0] * self.stride) + self.base_address

    def test_individual_access(self) -> None:
        """
        Test accessing individual array elements
        """
        for index in range(self.dimensions[0]):
            self.assertEqual(self.dut[index].address, self.calculate_address((index,)))

    def test_slice(self) -> None:
        """
        Test accessing slices of the array
        """

        full_slice = self.dut[:]

        for index in range(self.dimensions[0]):
            self.assertEqual(full_slice[index].address, self.calculate_address((index,)))

        even_slice = self.dut[::2]
        for index in range(self.dimensions[0]):
            if index % 2 == 0:
                self.assertEqual(even_slice[index].address, self.calculate_address((index,)))
            else:
                with self.assertRaises(IndexError):
                    _ = even_slice[index]

        odd_slice = self.dut[1::2]
        for index in range(self.dimensions[0]):
            if index % 2 == 1:
                self.assertEqual(odd_slice[index].address, self.calculate_address((index,)))
            else:
                with self.assertRaises(IndexError):
                    _ = odd_slice[index]

        subset_slice = self.dut[2:-2]
        for index in range(self.dimensions[0]):
            if index in range(2,self.dimensions[0]-2):
                self.assertEqual(subset_slice[index].address, self.calculate_address((index,)))
            else:
                with self.assertRaises(IndexError):
                    _ = subset_slice[index]

class Test2DArray(ArrayBase):
    """
    Test for 2D arrays
    """

    @property
    def dimensions(self) -> Tuple[int, ...]:
        return (10, 12,)

    @property
    def stride(self) -> int:
        return 4

    @property
    def base_address(self) -> int:
        return 0

    def calculate_address(self, indices: Tuple[int, ...]) -> int:
        return (indices[0] * self.dimensions[1] * self.stride) + \
               (indices[1] * self.stride) + self.base_address

    def test_individual_access(self) -> None:
        """
        Test accessing individual array elements
        """

        # do some spot checks
        self.assertEqual(self.dut[0, 0].address, self.calculate_address((0, 0)))
        self.assertEqual(self.dut[1, 1].address, self.calculate_address((1, 1)))
        self.assertEqual(self.dut[1, 2].address, self.calculate_address((1, 2)))

        with self.assertRaises(IndexError):
            _ = self.dut[10, 12]

        with self.assertRaises(IndexError):
            _ = self.dut[1]

        # sweep every item
        for index in product(*[range(dim) for dim in self.dimensions]):
            self.assertEqual(self.dut[index].address, self.calculate_address(index))

    def test_inner_slice_access(self) -> None:
        """
        Test accessing an inner slice of the array elements
        """

        inner_chunk = self.dut[0, :]
        for index, entry in enumerate(inner_chunk):
            self.assertEqual(entry.address, self.calculate_address((0, index)))

        _ = self.dut[0, 12:]

    def test_outer_slice_access(self) -> None:
        """
        Test accessing an outer slice of the array elements
        """

        outer_chunk = self.dut[:, 0]
        for index, entry in enumerate(outer_chunk):
            self.assertEqual(entry.address, self.calculate_address((index, 0)))

    def test_inner_section(self) -> None:
        """
        Test accessing an sub-section of the array
        """

        chunk = self.dut[2:-2, 3:-3]
        for index, entry in zip(product(range(2,8), range(3,9)), chunk):
            self.assertEqual(entry.address, self.calculate_address(index))

if __name__ == '__main__':
    unittest.main()
