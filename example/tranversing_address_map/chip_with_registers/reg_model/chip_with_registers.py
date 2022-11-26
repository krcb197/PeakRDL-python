"""Python Wrapper for the chip_with_registers register model

This code was generated from the PeakRDL-python package

"""
from enum import IntEnum, unique
from typing import Tuple
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union
from typing import cast

from ..lib import AddressMap, RegFile, Memory
from ..lib  import AddressMapArray, RegFileArray
from ..lib import MemoryReadOnlyArray, MemoryWriteOnlyArray, MemoryReadWriteArray
from ..lib import RegReadOnly, RegWriteOnly, RegReadWrite
from ..lib import RegReadOnlyArray, RegWriteOnlyArray, RegReadWriteArray
from ..lib import FieldReadOnly, FieldWriteOnly, FieldReadWrite
from ..lib import FieldSizeProps, FieldMiscProps, Field
from ..lib import ReadableRegister, WritableRegister
from ..lib import ReadableRegisterArray, WritableRegisterArray
from ..lib import CallbackSet












# root level enum definitions
@unique
class chip_with_registers_twoBitFieldType_enumcls(IntEnum):

    value1 = 0
    value2 = 1
    



# regfile, register and field definitions
        
    
class chip_with_registers_reg_Type_first_field_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """

    __slots__ : List[str] = []
    

        
    
class chip_with_registers_reg_Type_second_field_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """
    __enum_cls = chip_with_registers_twoBitFieldType_enumcls
    

    __slots__ : List[str] = []
    @property
    def enum_cls(self):
        """
        The enumeration class for this field
        """
        return self.__enum_cls
    def decode_read_value(self, value: int) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed and conversion to the enum associated with the
        field

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value

        Raises:
            ValueError - if the value read back for the field can not be matched to the enum
        """
        field_value = super().decode_read_value(value)

        return self.enum_cls(field_value)

    def read(self) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        read the register and then perform the necessary actions, to report the
        value as the enumeration including:

        * application of bit mask
        * bit shifting
        * converting integer value to enum

        Returns:
            field value
        """
        reg_value = self.parent_register.read()
        return self.decode_read_value(reg_value)
        
    def encode_write_value(self, value: chip_with_registers_twoBitFieldType_enumcls) -> int: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        return super().encode_write_value(value.value)

    def write(self, value : chip_with_registers_twoBitFieldType_enumcls) -> None: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        super().write(value.value)
        

    @property
    def default(self) -> Optional[chip_with_registers_twoBitFieldType_enumcls]:
        """
        The default value of the field

        This returns None:
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        int_default = super().default

        if int_default is not None:
            return chip_with_registers_twoBitFieldType_enumcls(int_default)

        return None
    
    

        
class chip_with_registers_reg_Type_cls(RegReadWrite):
    """
    Class to represent a register in the register model

    
    """

    __slots__ : List[str] = ['__first_field', '__second_field']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap,RegFile,Memory]):

        super().__init__(callbacks=callbacks,
                         address=address,
                         accesswidth=32,
                         width=32,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__first_field = chip_with_registers_reg_Type_first_field_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=16,
                lsb=0,
                msb=15,
                low=0,
                high=15),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.first_field',
            inst_name='first_field')
        self.__second_field = chip_with_registers_reg_Type_second_field_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=2,
                lsb=16,
                msb=17,
                low=16,
                high=17),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.second_field',
            inst_name='second_field')

    
    def read_fields(self):
        """
        read the register and return a dictionary of the field values
        """
        reg_value = self.read()

        return_dict = {
                        'first_field' : self.first_field.decode_read_value(reg_value),
                        'second_field' : self.second_field.decode_read_value(reg_value)
                      }

        return return_dict

    @property
    def readable_fields(self) -> Iterator[Union[FieldReadOnly, FieldReadWrite]]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    

    
    @property
    def writable_fields(self) -> Iterator[Union[FieldWriteOnly, FieldReadWrite]]:
        """
        generator that produces has all the writable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    
    def write_fields(self, **kwargs) -> None:  # type
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """

        if len(kwargs) == 0:
            raise ValueError('no command args')

        bit_mask = 0
        reg_value = 0
        if 'first_field' in kwargs:
            reg_value |= self.first_field.encode_write_value(kwargs['first_field'])
            bit_mask |= self.first_field.bitmask
            kwargs.pop('first_field')
        if 'second_field' in kwargs:
            reg_value |= self.second_field.encode_write_value(kwargs['second_field'])
            bit_mask |= self.second_field.bitmask
            kwargs.pop('second_field')
        if len(kwargs) != 0:
            # left over unhandled arguments
            raise ValueError('unrecognised arguments in field')

        inverse_bit_mask = self.max_value ^ bit_mask

        self.write((self.read() & inverse_bit_mask) | reg_value)

    
    

    # build the properties for the fields
    @property
    def first_field(self) -> chip_with_registers_reg_Type_first_field_cls:
        """
        Property to access first_field field of the register

        
        """
        return self.__first_field
        
    @property
    def second_field(self) -> chip_with_registers_reg_Type_second_field_cls:
        """
        Property to access second_field field of the register

        
        """
        return self.__second_field
        
    

        
    
class chip_with_registers_reg_Type_first_field_0x0x175238b504_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """

    __slots__ : List[str] = []
    

        
    
class chip_with_registers_reg_Type_second_field_0x0x175238b537_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """
    __enum_cls = chip_with_registers_twoBitFieldType_enumcls
    

    __slots__ : List[str] = []
    @property
    def enum_cls(self):
        """
        The enumeration class for this field
        """
        return self.__enum_cls
    def decode_read_value(self, value: int) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed and conversion to the enum associated with the
        field

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value

        Raises:
            ValueError - if the value read back for the field can not be matched to the enum
        """
        field_value = super().decode_read_value(value)

        return self.enum_cls(field_value)

    def read(self) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        read the register and then perform the necessary actions, to report the
        value as the enumeration including:

        * application of bit mask
        * bit shifting
        * converting integer value to enum

        Returns:
            field value
        """
        reg_value = self.parent_register.read()
        return self.decode_read_value(reg_value)
        
    def encode_write_value(self, value: chip_with_registers_twoBitFieldType_enumcls) -> int: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        return super().encode_write_value(value.value)

    def write(self, value : chip_with_registers_twoBitFieldType_enumcls) -> None: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        super().write(value.value)
        

    @property
    def default(self) -> Optional[chip_with_registers_twoBitFieldType_enumcls]:
        """
        The default value of the field

        This returns None:
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        int_default = super().default

        if int_default is not None:
            return chip_with_registers_twoBitFieldType_enumcls(int_default)

        return None
    
    

        
class chip_with_registers_reg_Type_0x0x175238b385_cls(RegReadWrite):
    """
    Class to represent a register in the register model

    
    """

    __slots__ : List[str] = ['__first_field', '__second_field']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap,RegFile,Memory]):

        super().__init__(callbacks=callbacks,
                         address=address,
                         accesswidth=32,
                         width=32,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__first_field = chip_with_registers_reg_Type_first_field_0x0x175238b504_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=16,
                lsb=0,
                msb=15,
                low=0,
                high=15),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.first_field',
            inst_name='first_field')
        self.__second_field = chip_with_registers_reg_Type_second_field_0x0x175238b537_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=2,
                lsb=16,
                msb=17,
                low=16,
                high=17),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.second_field',
            inst_name='second_field')

    
    def read_fields(self):
        """
        read the register and return a dictionary of the field values
        """
        reg_value = self.read()

        return_dict = {
                        'first_field' : self.first_field.decode_read_value(reg_value),
                        'second_field' : self.second_field.decode_read_value(reg_value)
                      }

        return return_dict

    @property
    def readable_fields(self) -> Iterator[Union[FieldReadOnly, FieldReadWrite]]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    

    
    @property
    def writable_fields(self) -> Iterator[Union[FieldWriteOnly, FieldReadWrite]]:
        """
        generator that produces has all the writable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    
    def write_fields(self, **kwargs) -> None:  # type
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """

        if len(kwargs) == 0:
            raise ValueError('no command args')

        bit_mask = 0
        reg_value = 0
        if 'first_field' in kwargs:
            reg_value |= self.first_field.encode_write_value(kwargs['first_field'])
            bit_mask |= self.first_field.bitmask
            kwargs.pop('first_field')
        if 'second_field' in kwargs:
            reg_value |= self.second_field.encode_write_value(kwargs['second_field'])
            bit_mask |= self.second_field.bitmask
            kwargs.pop('second_field')
        if len(kwargs) != 0:
            # left over unhandled arguments
            raise ValueError('unrecognised arguments in field')

        inverse_bit_mask = self.max_value ^ bit_mask

        self.write((self.read() & inverse_bit_mask) | reg_value)

    
    

    # build the properties for the fields
    @property
    def first_field(self) -> chip_with_registers_reg_Type_first_field_0x0x175238b504_cls:
        """
        Property to access first_field field of the register

        
        """
        return self.__first_field
        
    @property
    def second_field(self) -> chip_with_registers_reg_Type_second_field_0x0x175238b537_cls:
        """
        Property to access second_field field of the register

        
        """
        return self.__second_field
        
class chip_with_registers_reg_Type_0x0x175238b385_array_cls(RegReadWriteArray):
    """
    Class to represent a register array in the register model
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, Memory],
                 elements: Tuple[chip_with_registers_reg_Type_0x0x175238b385_cls, ...]):

        for element in elements:
            if not isinstance(element, chip_with_registers_reg_Type_0x0x175238b385_cls):
                raise TypeError(f'All Elements should be of type chip_with_registers_reg_Type_0x0x175238b385_cls, '
                                f'found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item) -> Union[chip_with_registers_reg_Type_0x0x175238b385_cls, Tuple[chip_with_registers_reg_Type_0x0x175238b385_cls, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[chip_with_registers_reg_Type_0x0x175238b385_cls, Tuple[chip_with_registers_reg_Type_0x0x175238b385_cls, ...]], super().__getitem__(item))
    

        
class chip_with_registers_regfile_Type_cls(RegFile):
    """
    Class to represent a register file in the register model

    
    """

    __slots__ : List[str] = ['__single_reg', '__reg_array']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle:str,
                 inst_name:str,
                 parent:Union[AddressMap,RegFile]):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # instance of objects within the class
        
            
        self.__single_reg = chip_with_registers_reg_Type_cls(callbacks=callbacks,
                                                                     address=self.address+0,
                                                                     logger_handle=logger_handle+'.single_reg',
                                                                                       inst_name='single_reg', parent=self)
        
            
        self.__reg_array = chip_with_registers_reg_Type_0x0x175238b385_array_cls(elements=( 
                                                                                                 chip_with_registers_reg_Type_0x0x175238b385_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(0 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[0]',
                                                                                                 inst_name='reg_array[0]', parent=self),
                                                                                                 chip_with_registers_reg_Type_0x0x175238b385_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(1 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[1]',
                                                                                                 inst_name='reg_array[1]', parent=self),
                                                                                                 chip_with_registers_reg_Type_0x0x175238b385_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(2 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[2]',
                                                                                                 inst_name='reg_array[2]', parent=self),
                                                                                                 chip_with_registers_reg_Type_0x0x175238b385_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(3 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[3]',
                                                                                                 inst_name='reg_array[3]', parent=self) ),
                                                                                      logger_handle=logger_handle+'.reg_array',
                                                                                      inst_name='reg_array', parent=self)
        

    # properties for Register and RegisterFiles
    @property
    def single_reg(self) -> chip_with_registers_reg_Type_cls:
        """
        Property to access single_reg 

        
        """
        return self.__single_reg
    
    @property
    def reg_array(self) -> chip_with_registers_reg_Type_0x0x175238b385_array_cls:
        """
        Property to access reg_array array

        
        """
        return self.__reg_array
    

    

    def get_readable_registers(self, unroll=False) -> Iterator[Union[ReadableRegister, Tuple[ReadableRegister, ...]]]:
        """
        generator that produces all the readable_registers of this node
        """
        
                
                    
        yield cast(ReadableRegister, self.single_reg)
                
                    
        if unroll:
            for child in self.reg_array:
                yield cast(ReadableRegister, child)
        else:
            yield cast(Tuple[ReadableRegister, ...], self.reg_array)
                    

        # Empty generator in case there are no children of this type
        if False: yield

    def get_writable_registers(self, unroll=False) -> Iterator[Union[WritableRegister, Tuple[WritableRegister, ...]]]:
        """
        generator that produces all the readable_registers of this node
        """
        
                
                    
        yield cast(WritableRegister, self.single_reg)
                
                    
        if unroll:
            for child in self.reg_array:
                yield cast(WritableRegister, child)
        else:
            yield cast(Tuple[WritableRegister, ...], self.reg_array)
                    

        # Empty generator in case there are no children of this type
        if False: yield
    
    def get_sections(self, unroll=False) -> Iterator[Union[RegFile,Tuple[RegFile,...]]]:
        """
        generator that produces all the RegFile children of this node
        """
        

        # Empty generator in case there are no children of this type
        if False: yield
class chip_with_registers_regfile_Type_array_cls(RegFileArray):
    """
    Class to represent a regfile array in the register model
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[AddressMap, RegFile],
                 elements: Tuple[chip_with_registers_regfile_Type_cls, ...]):

        for element in elements:
            if not isinstance(element, chip_with_registers_regfile_Type_cls):
                raise TypeError(f'All Elements should be of type chip_with_registers_regfile_Type_cls, '
                                f'found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item) -> Union[chip_with_registers_regfile_Type_cls, Tuple[chip_with_registers_regfile_Type_cls, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[chip_with_registers_regfile_Type_cls, Tuple[chip_with_registers_regfile_Type_cls, ...]], super().__getitem__(item))
    

        
    
class chip_with_registers_reg_Type_first_field_0x0x175238b58e_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """

    __slots__ : List[str] = []
    

        
    
class chip_with_registers_reg_Type_second_field_0x0x175238b5c1_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """
    __enum_cls = chip_with_registers_twoBitFieldType_enumcls
    

    __slots__ : List[str] = []
    @property
    def enum_cls(self):
        """
        The enumeration class for this field
        """
        return self.__enum_cls
    def decode_read_value(self, value: int) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed and conversion to the enum associated with the
        field

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value

        Raises:
            ValueError - if the value read back for the field can not be matched to the enum
        """
        field_value = super().decode_read_value(value)

        return self.enum_cls(field_value)

    def read(self) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        read the register and then perform the necessary actions, to report the
        value as the enumeration including:

        * application of bit mask
        * bit shifting
        * converting integer value to enum

        Returns:
            field value
        """
        reg_value = self.parent_register.read()
        return self.decode_read_value(reg_value)
        
    def encode_write_value(self, value: chip_with_registers_twoBitFieldType_enumcls) -> int: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        return super().encode_write_value(value.value)

    def write(self, value : chip_with_registers_twoBitFieldType_enumcls) -> None: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        super().write(value.value)
        

    @property
    def default(self) -> Optional[chip_with_registers_twoBitFieldType_enumcls]:
        """
        The default value of the field

        This returns None:
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        int_default = super().default

        if int_default is not None:
            return chip_with_registers_twoBitFieldType_enumcls(int_default)

        return None
    
    

        
class chip_with_registers_reg_Type_0x0x175238b585_cls(RegReadWrite):
    """
    Class to represent a register in the register model

    
    """

    __slots__ : List[str] = ['__first_field', '__second_field']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap,RegFile,Memory]):

        super().__init__(callbacks=callbacks,
                         address=address,
                         accesswidth=32,
                         width=32,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__first_field = chip_with_registers_reg_Type_first_field_0x0x175238b58e_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=16,
                lsb=0,
                msb=15,
                low=0,
                high=15),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.first_field',
            inst_name='first_field')
        self.__second_field = chip_with_registers_reg_Type_second_field_0x0x175238b5c1_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=2,
                lsb=16,
                msb=17,
                low=16,
                high=17),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.second_field',
            inst_name='second_field')

    
    def read_fields(self):
        """
        read the register and return a dictionary of the field values
        """
        reg_value = self.read()

        return_dict = {
                        'first_field' : self.first_field.decode_read_value(reg_value),
                        'second_field' : self.second_field.decode_read_value(reg_value)
                      }

        return return_dict

    @property
    def readable_fields(self) -> Iterator[Union[FieldReadOnly, FieldReadWrite]]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    

    
    @property
    def writable_fields(self) -> Iterator[Union[FieldWriteOnly, FieldReadWrite]]:
        """
        generator that produces has all the writable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    
    def write_fields(self, **kwargs) -> None:  # type
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """

        if len(kwargs) == 0:
            raise ValueError('no command args')

        bit_mask = 0
        reg_value = 0
        if 'first_field' in kwargs:
            reg_value |= self.first_field.encode_write_value(kwargs['first_field'])
            bit_mask |= self.first_field.bitmask
            kwargs.pop('first_field')
        if 'second_field' in kwargs:
            reg_value |= self.second_field.encode_write_value(kwargs['second_field'])
            bit_mask |= self.second_field.bitmask
            kwargs.pop('second_field')
        if len(kwargs) != 0:
            # left over unhandled arguments
            raise ValueError('unrecognised arguments in field')

        inverse_bit_mask = self.max_value ^ bit_mask

        self.write((self.read() & inverse_bit_mask) | reg_value)

    
    

    # build the properties for the fields
    @property
    def first_field(self) -> chip_with_registers_reg_Type_first_field_0x0x175238b58e_cls:
        """
        Property to access first_field field of the register

        
        """
        return self.__first_field
        
    @property
    def second_field(self) -> chip_with_registers_reg_Type_second_field_0x0x175238b5c1_cls:
        """
        Property to access second_field field of the register

        
        """
        return self.__second_field
        
    

        
    
class chip_with_registers_reg_Type_first_field_0x0x175238b5fd_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """

    __slots__ : List[str] = []
    

        
    
class chip_with_registers_reg_Type_second_field_0x0x175238b934_cls(FieldReadWrite):
    
    """
    Class to represent a register field in the register model

    
    """
    __enum_cls = chip_with_registers_twoBitFieldType_enumcls
    

    __slots__ : List[str] = []
    @property
    def enum_cls(self):
        """
        The enumeration class for this field
        """
        return self.__enum_cls
    def decode_read_value(self, value: int) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed and conversion to the enum associated with the
        field

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value

        Raises:
            ValueError - if the value read back for the field can not be matched to the enum
        """
        field_value = super().decode_read_value(value)

        return self.enum_cls(field_value)

    def read(self) -> chip_with_registers_twoBitFieldType_enumcls:
        """
        read the register and then perform the necessary actions, to report the
        value as the enumeration including:

        * application of bit mask
        * bit shifting
        * converting integer value to enum

        Returns:
            field value
        """
        reg_value = self.parent_register.read()
        return self.decode_read_value(reg_value)
        
    def encode_write_value(self, value: chip_with_registers_twoBitFieldType_enumcls) -> int: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        return super().encode_write_value(value.value)

    def write(self, value : chip_with_registers_twoBitFieldType_enumcls) -> None: # type: ignore[override]

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an chip_with_registers_twoBitFieldType_enumcls but got %s' % type(value))

        super().write(value.value)
        

    @property
    def default(self) -> Optional[chip_with_registers_twoBitFieldType_enumcls]:
        """
        The default value of the field

        This returns None:
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        int_default = super().default

        if int_default is not None:
            return chip_with_registers_twoBitFieldType_enumcls(int_default)

        return None
    
    

        
class chip_with_registers_reg_Type_0x0x175238b588_cls(RegReadWrite):
    """
    Class to represent a register in the register model

    
    """

    __slots__ : List[str] = ['__first_field', '__second_field']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap,RegFile,Memory]):

        super().__init__(callbacks=callbacks,
                         address=address,
                         accesswidth=32,
                         width=32,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # build the field attributes
        self.__first_field = chip_with_registers_reg_Type_first_field_0x0x175238b5fd_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=16,
                lsb=0,
                msb=15,
                low=0,
                high=15),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.first_field',
            inst_name='first_field')
        self.__second_field = chip_with_registers_reg_Type_second_field_0x0x175238b934_cls(
            parent_register=self,
            size_props=FieldSizeProps(
                width=2,
                lsb=16,
                msb=17,
                low=16,
                high=17),
            misc_props=FieldMiscProps(
                default=0,
                is_volatile=False),
            logger_handle=logger_handle+'.second_field',
            inst_name='second_field')

    
    def read_fields(self):
        """
        read the register and return a dictionary of the field values
        """
        reg_value = self.read()

        return_dict = {
                        'first_field' : self.first_field.decode_read_value(reg_value),
                        'second_field' : self.second_field.decode_read_value(reg_value)
                      }

        return return_dict

    @property
    def readable_fields(self) -> Iterator[Union[FieldReadOnly, FieldReadWrite]]:
        """
        generator that produces has all the readable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    

    
    @property
    def writable_fields(self) -> Iterator[Union[FieldWriteOnly, FieldReadWrite]]:
        """
        generator that produces has all the writable fields within the register
        """
        yield self.first_field
        yield self.second_field
        

    
    def write_fields(self, **kwargs) -> None:  # type
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """

        if len(kwargs) == 0:
            raise ValueError('no command args')

        bit_mask = 0
        reg_value = 0
        if 'first_field' in kwargs:
            reg_value |= self.first_field.encode_write_value(kwargs['first_field'])
            bit_mask |= self.first_field.bitmask
            kwargs.pop('first_field')
        if 'second_field' in kwargs:
            reg_value |= self.second_field.encode_write_value(kwargs['second_field'])
            bit_mask |= self.second_field.bitmask
            kwargs.pop('second_field')
        if len(kwargs) != 0:
            # left over unhandled arguments
            raise ValueError('unrecognised arguments in field')

        inverse_bit_mask = self.max_value ^ bit_mask

        self.write((self.read() & inverse_bit_mask) | reg_value)

    
    

    # build the properties for the fields
    @property
    def first_field(self) -> chip_with_registers_reg_Type_first_field_0x0x175238b5fd_cls:
        """
        Property to access first_field field of the register

        
        """
        return self.__first_field
        
    @property
    def second_field(self) -> chip_with_registers_reg_Type_second_field_0x0x175238b934_cls:
        """
        Property to access second_field field of the register

        
        """
        return self.__second_field
        
class chip_with_registers_reg_Type_0x0x175238b588_array_cls(RegReadWriteArray):
    """
    Class to represent a register array in the register model
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, Memory],
                 elements: Tuple[chip_with_registers_reg_Type_0x0x175238b588_cls, ...]):

        for element in elements:
            if not isinstance(element, chip_with_registers_reg_Type_0x0x175238b588_cls):
                raise TypeError(f'All Elements should be of type chip_with_registers_reg_Type_0x0x175238b588_cls, '
                                f'found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item) -> Union[chip_with_registers_reg_Type_0x0x175238b588_cls, Tuple[chip_with_registers_reg_Type_0x0x175238b588_cls, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[chip_with_registers_reg_Type_0x0x175238b588_cls, Tuple[chip_with_registers_reg_Type_0x0x175238b588_cls, ...]], super().__getitem__(item))
    

        
class chip_with_registers_regfile_Type_0x0x175238b08e_cls(RegFile):
    """
    Class to represent a register file in the register model

    
    """

    __slots__ : List[str] = ['__single_reg', '__reg_array']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle:str,
                 inst_name:str,
                 parent:Union[AddressMap,RegFile]):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        # instance of objects within the class
        
            
        self.__single_reg = chip_with_registers_reg_Type_0x0x175238b585_cls(callbacks=callbacks,
                                                                     address=self.address+0,
                                                                     logger_handle=logger_handle+'.single_reg',
                                                                                       inst_name='single_reg', parent=self)
        
            
        self.__reg_array = chip_with_registers_reg_Type_0x0x175238b588_array_cls(elements=( 
                                                                                                 chip_with_registers_reg_Type_0x0x175238b588_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(0 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[0]',
                                                                                                 inst_name='reg_array[0]', parent=self),
                                                                                                 chip_with_registers_reg_Type_0x0x175238b588_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(1 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[1]',
                                                                                                 inst_name='reg_array[1]', parent=self),
                                                                                                 chip_with_registers_reg_Type_0x0x175238b588_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(2 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[2]',
                                                                                                 inst_name='reg_array[2]', parent=self),
                                                                                                 chip_with_registers_reg_Type_0x0x175238b588_cls(callbacks=callbacks,
                                                                                                 address=self.address+4+(3 * 4),
                                                                                                 logger_handle=logger_handle+'.reg_array[3]',
                                                                                                 inst_name='reg_array[3]', parent=self) ),
                                                                                      logger_handle=logger_handle+'.reg_array',
                                                                                      inst_name='reg_array', parent=self)
        

    # properties for Register and RegisterFiles
    @property
    def single_reg(self) -> chip_with_registers_reg_Type_0x0x175238b585_cls:
        """
        Property to access single_reg 

        
        """
        return self.__single_reg
    
    @property
    def reg_array(self) -> chip_with_registers_reg_Type_0x0x175238b588_array_cls:
        """
        Property to access reg_array array

        
        """
        return self.__reg_array
    

    

    def get_readable_registers(self, unroll=False) -> Iterator[Union[ReadableRegister, Tuple[ReadableRegister, ...]]]:
        """
        generator that produces all the readable_registers of this node
        """
        
                
                    
        yield cast(ReadableRegister, self.single_reg)
                
                    
        if unroll:
            for child in self.reg_array:
                yield cast(ReadableRegister, child)
        else:
            yield cast(Tuple[ReadableRegister, ...], self.reg_array)
                    

        # Empty generator in case there are no children of this type
        if False: yield

    def get_writable_registers(self, unroll=False) -> Iterator[Union[WritableRegister, Tuple[WritableRegister, ...]]]:
        """
        generator that produces all the readable_registers of this node
        """
        
                
                    
        yield cast(WritableRegister, self.single_reg)
                
                    
        if unroll:
            for child in self.reg_array:
                yield cast(WritableRegister, child)
        else:
            yield cast(Tuple[WritableRegister, ...], self.reg_array)
                    

        # Empty generator in case there are no children of this type
        if False: yield
    
    def get_sections(self, unroll=False) -> Iterator[Union[RegFile,Tuple[RegFile,...]]]:
        """
        generator that produces all the RegFile children of this node
        """
        

        # Empty generator in case there are no children of this type
        if False: yield
    

        
class chip_with_registers_cls(AddressMap):
    """
    Class to represent a address map in the register model

    
    """

    __slots__ : List[str] = ['__regfile_array', '__single_regfile']

    def __init__(self,
                 callbacks: CallbackSet,
                 address:int=0,
                 logger_handle:str='reg_model.chip_with_registers',
                 inst_name='chip_with_registers',
                 parent:Optional[AddressMap]=None):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        
        self.__regfile_array = chip_with_registers_regfile_Type_array_cls( elements=( 
                                                                                                    chip_with_registers_regfile_Type_cls(callbacks=callbacks,
                                                                                                                                                address=self.address+0+(0 * 20),
                                                                                                                                                logger_handle=logger_handle+'.regfile_array[0]',
                                                                                                                                                inst_name='regfile_array[0]', parent=self),
                                                                                                    chip_with_registers_regfile_Type_cls(callbacks=callbacks,
                                                                                                                                                address=self.address+0+(1 * 20),
                                                                                                                                                logger_handle=logger_handle+'.regfile_array[1]',
                                                                                                                                                inst_name='regfile_array[1]', parent=self) ),
                                                                                        logger_handle=logger_handle+'.regfile_array',
                                                                                        inst_name='regfile_array', parent=self)
        self.__single_regfile = chip_with_registers_regfile_Type_0x0x175238b08e_cls(callbacks=callbacks,
                                                                                address=self.address+64,
                                                                                logger_handle=logger_handle+'.single_regfile',
                                                                                inst_name='single_regfile', parent=self)
        
    @property
    def regfile_array(self) -> chip_with_registers_regfile_Type_array_cls:
        """
        Property to access regfile_array array

        
        """
        return self.__regfile_array
        
    @property
    def single_regfile(self) -> chip_with_registers_regfile_Type_0x0x175238b08e_cls:
        """
        Property to access single_regfile 

        
        """
        return self.__single_regfile
        

    

    def get_readable_registers(self, unroll=False) -> Iterator[Union[ReadableRegister, Tuple[ReadableRegister, ...]]]:
        """
        generator that produces all the readable_registers of this node
        """
        

        # Empty generator in case there are no children of this type
        if False: yield

    def get_writable_registers(self, unroll=False) -> Iterator[Union[WritableRegister, Tuple[WritableRegister, ...]]]:
        """
        generator that produces all the readable_registers of this node
        """
        

        # Empty generator in case there are no children of this type
        if False: yield
    
    def get_memories(self, unroll=False) -> Iterator[Union[Memory,Tuple[Memory,...]]]:
        """
        generator that produces all the Memory children of this node
        """
        

        # Empty generator in case there are no children of this type
        if False: yield
    
    def get_sections(self, unroll=False) -> Iterator[Union[Union[AddressMap, RegFile],Tuple[Union[AddressMap, RegFile],...]]]:
        """
        generator that produces all the Union[AddressMap, RegFile] children of this node
        """
        
        if unroll:
            for child in self.regfile_array:
                yield cast(Union[AddressMap, RegFile], child)
        else:
            yield cast(Tuple[Union[AddressMap, RegFile],...], self.regfile_array)
        
        yield cast(Union[AddressMap, RegFile], self.single_regfile)

        # Empty generator in case there are no children of this type
        if False: yield
    



if __name__ == '__main__':
    # dummy functions to demonstrate the class
    def read_addr_space(addr: int, width: int, accesswidth: int) -> int:
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
        return int(input('value to read from address:0x%X'%addr))

    def write_addr_space(addr: int, width: int, accesswidth: int, data: int) -> None:
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
        print('write data:0x%X to address:0x%X'%(data, addr))

    # create an instance of the class
    chip_with_registers = chip_with_registers_cls(callbacks = CallbackSet(read_callback=read_addr_space,
                                                                                                     write_callback=write_addr_space))