import unittest
from typing import List, Generator, Iterator, Dict, Type, Tuple
from abc import ABC, abstractmethod
from contextlib import contextmanager
from itertools import product

from peakrdl_python.lib import RegReadOnlyArray, FieldReadOnly, RegReadOnly, \
    NormalCallbackSet, AddressMap, FieldMiscProps, FieldSizeProps, Node

class FieldToTest(FieldReadOnly):
    """
    Class to represent a register field in the register model
    """
    __slots__: List[str] = []


class RegisterToTest(RegReadOnly):
    """
    Class to represent a register in the register model
    """
    __slots__: List[str] = ['__field']

    def __init__(self,
                 callbacks: NormalCallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):
        super().__init__(callbacks=callbacks,
                         address=address,
                         accesswidth=32,
                         width=32,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__field: FieldToTest = FieldToTest(
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

    @contextmanager
    def single_read(self) -> Generator['RegisterToTest', None, None]:
        """
        Context Manager to do multiple accesses using a single read operation
        """
        with super().single_read() as reg:
            yield cast('basic_basicreg_c_cls', reg)

    # build the properties for the fields
    @property
    def field_(self) -> FieldToTest:
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

class RegisterArrayToTest(RegReadOnlyArray):
    """
    Class to represent a register array in the register model
    """
    __slots__: List[str] = []

    @property
    def _element_datatype(self) -> Type[Node]:
        return RegisterToTest


class ArrayBase(unittest.TestCase, ABC):

    @property
    @abstractmethod
    def dimensions(self) -> int:
        pass

    @property
    @abstractmethod
    def base_address(self) -> int:
        pass

    @property
    @abstractmethod
    def stride(self) -> int:
        pass

    @property
    def dut(self) -> RegisterArrayToTest:
        return self.__dut

    @abstractmethod
    def calculate_address(self, indices: Tuple[int, ...]) -> int:
        ...

    def setUp(self) -> None:
        self.__dut = RegisterArrayToTest(logger_handle='dut',
                                       inst_name='dut',
                                       parent=None,
                                       callbacks=NormalCallbackSet(),
                                       address=self.base_address,
                                       stride=self.stride,
                                       dimensions=self.dimensions)


class Test1DArray(ArrayBase):

    @property
    def dimensions(self) -> int:
        return (10,)

    @property
    def stride(self) -> int:
        return 4

    @property
    def base_address(self) -> int:
        return 0

    def calculate_address(self, indices: Tuple[int, ...]) -> int:
        return (indices[0] * self.stride) + self.base_address

    def test_individual_access(self):
        for index in range(self.dimensions[0]):
            self.assertEqual(self.dut[index].address, self.calculate_address((index,)))

    def test_slice(self):

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

    @property
    def dimensions(self) -> int:
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

    def test_individual_access(self):

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

    def test_inner_slice_access(self):

        inner_chunk = self.dut[0, :]
        for index, entry in enumerate(inner_chunk):
            self.assertEqual(entry.address, self.calculate_address((0, index)))

        _ = self.dut[0, 12:]

    def test_outer_slice_access(self):

        outer_chunk = self.dut[:, 0]
        for index, entry in enumerate(outer_chunk):
            self.assertEqual(entry.address, self.calculate_address((index, 0)))

    def test_inner_section(self):

        chunk = self.dut[2:-2, 3:-3]
        for index, entry in zip(product(range(2,8), range(3,9)), chunk):
            self.assertEqual(entry.address, self.calculate_address(index))

if __name__ == '__main__':
    unittest.main()
