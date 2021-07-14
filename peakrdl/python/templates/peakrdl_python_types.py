
import logging
from typing import Callable, TypeVar

read_callback_type = Callable[[int], int]
write_callback_type = Callable[[int, int], type(None)]


class _Base:

    __slots__ = ['__logger']

    def __init__(self, logger_handle):
        self.__logger = logging.getLogger(logger_handle)
        self._logger.info(f'creating instance of {self.__class__}')

    @property
    def _logger(self):
        return self.__logger


class _Node(_Base):
    __slots__ = ['__base_address', '__address_width', '__data_width']

    def __init__(self, base_address, address_width, data_width, logger_handle):
        super().__init__(logger_handle=logger_handle)
        self.__base_address = base_address
        self.__address_width = address_width
        self.__data_width = data_width

    @property
    def base_address(self):
        return self.__base_address

    @property
    def address_width(self):
        return self.__address_width

    @property
    def data_width(self):
        """
        width of the data register
        """
        return self.__data_width


class AddressMap(_Node):

    __slots__ = []

    pass


class RegFile(_Node):

    __slots__ = []


class Reg(_Node):

    __slots__ = []

    @property
    def max_value(self):
        return (2 ** self.data_width) - 1


class RegReadOnly(Reg):

    __slots__ = ['__read_callback']

    def __init__(self, read_callback: read_callback_type, base_address, address_width, data_width, logger_handle):
        super().__init__(base_address=base_address, address_width=address_width, data_width=data_width,
                         logger_handle=logger_handle)
        self.__read_callback = read_callback

    def read(self):
        return self.__read_callback(self.base_address)


class RegWriteOnly(Reg):

    __slots__ = ['__write_callback']

    def __init__(self, write_callback: write_callback_type, base_address, address_width, data_width, logger_handle):
        super().__init__(base_address=base_address, address_width=address_width, data_width=data_width,
                         logger_handle=logger_handle)
        self.__write_callback = write_callback

    def write(self, data):

        if data > self.max_value:
            raise ValueError('data out of range')

        if data < 0:
            raise ValueError('data out of range')

        self._logger.info(f'Writing data:{data:X} to address:{self.base_address:X}')

        self.__write_callback(self.base_address, data)


class RegReadWrite(Reg):

    __slots__ = ['__write_callback', '__read_callback']

    def __init__(self, write_callback: write_callback_type, read_callback: read_callback_type,
                 base_address, address_width, data_width, logger_handle):
        super().__init__(base_address=base_address, address_width=address_width, data_width=data_width,
                         logger_handle=logger_handle)
        self.__write_callback = write_callback
        self.__read_callback = read_callback

    def write(self, data):

        if data > self.max_value:
            raise ValueError('data out of range')

        if data < 0:
            raise ValueError('data out of range')

        self._logger.info(f'Writing data:0x{data:X} to address:0x{self.base_address:X}')

        self.__write_callback(self.base_address, data)

    def read(self):
        return self.__read_callback(self.base_address)


class Field(_Base):

    __slots__ = ['__parent_register', '__msb', '__lsb', '__bitmask']

    def __init__(self, parent_register: Reg, msb: int, lsb: int, logger_handle: str):

        super().__init__(logger_handle=logger_handle)

        if not isinstance(parent_register, Reg):
            raise TypeError('parent register must be of type reg_cls but got %s' % type(parent_register))
        self.__parent_register = parent_register

        if msb < lsb:
            raise ValueError('field msb can not be less than the lsb')

        self.__msb = msb
        self.__lsb = lsb

        self.__bitmask = 0
        for bit_position in range(self.__lsb, self.__msb+1):
            self.__bitmask |= (1 << bit_position)

    @property
    def parent_register(self) -> Reg:
        return self.__parent_register

    @property
    def lsb(self) -> int:
        return self.__lsb

    @property
    def msb(self) -> int:
        return self.__msb

    @property
    def field_width(self) -> int:
        return self.msb - self.lsb + 1

    @property
    def max_value(self):
        return (2 ** self.field_width) - 1

    @property
    def bitmask(self):
        return self.__bitmask

    @property
    def register_data_width(self):
        return self.parent_register.data_width

    @property
    def inverse_bitmask(self):
        return self.parent_register.max_value ^ self.bitmask


readable_reg_type = TypeVar('readable_reg_type', RegReadOnly, RegReadWrite)


class FieldReadOnly(Field):

    __slots__ = []

    def __init__(self, parent_register: readable_reg_type, msb: int, lsb: int, logger_handle: str):

        if not isinstance(parent_register, (RegReadWrite, RegReadOnly)):
            raise TypeError('parent register must be of type reg_cls but got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle, msb=msb, lsb=lsb, parent_register=parent_register)

    def read(self):
        return (self.parent_register.read() & self.bitmask) >> self.lsb

    @Field.parent_register.getter
    def parent_register(self) -> readable_reg_type:
        assert isinstance(super().parent_register, (RegReadOnly, RegReadWrite))
        return super().parent_register


writeable_reg_type = TypeVar('writeable_reg_type', RegWriteOnly, RegReadWrite)


class FieldWriteOnly(Field):

    __slots__ = []

    def __init__(self, parent_register: writeable_reg_type, msb: int, lsb: int, logger_handle: str):

        if not isinstance(parent_register, (RegReadWrite, RegWriteOnly)):
            raise TypeError('parent register must be of type reg_cls but got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle, msb=msb, lsb=lsb, parent_register=parent_register)

    def write(self, value):
        # TODO need to consider what makes sense here, the following special cases can be handled
        #      * field is the same width as the reg
        #      * there is only one field in the reg
        #      other case don't make that much sense
        raise NotImplementedError('Need to make a decision about what behaviour happens here')

    @Field.parent_register.getter
    def parent_register(self) -> writeable_reg_type:
        return super().parent_register


class FieldReadWrite(FieldReadOnly, FieldWriteOnly):

    __slots__ = []

    def __init__(self, parent_register: RegReadWrite, msb: int, lsb: int, logger_handle: str):

        if not isinstance(parent_register, RegReadWrite):
            raise TypeError('parent register must be of type reg_cls but got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle, msb=msb, lsb=lsb, parent_register=parent_register)

    def write(self, value):

        if not isinstance(value, int):
            raise TypeError('value must be an int but got %s' % type(value))

        if value < 0:
            raise ValueError('value to be written to register must be greater than or equal to 0')

        if value > self.max_value:
            raise ValueError('value to be written to register must be less than or equal to %d' % self.max_value)

        if (self.msb == (self.parent_register.data_width-1)) and (self.lsb == 0):
            # special case where the field occupies the whole register, there a straight write can be performed
            new_reg_value = value
        else:
            # do a read, modify write
            reg_value = self.parent_register.read()

            new_reg_value = (reg_value & self.inverse_bitmask) | (value << self.lsb)

        self.parent_register.write(new_reg_value)

    @Field.parent_register.getter
    def parent_register(self) -> RegReadWrite:
        return super().parent_register


class EnumField(Field):

    __slots__ = ['__enum_cls']

    def __init__(self, parent_register: Reg, msb: int, lsb: int, encoding_enum, logger_handle):

        super().__init__(parent_register=parent_register,
                         msb=msb,
                         lsb=lsb,
                         logger_handle=logger_handle)

        self.__enum_cls = encoding_enum

    @property
    def enum_cls(self):
        return self.__enum_cls


class EnumFieldReadOnly(EnumField):

    __slots__ = []

    def __init__(self, parent_register: readable_reg_type, msb: int, lsb: int, encoding_enum, logger_handle: str):

        if not isinstance(parent_register, (RegReadWrite, RegReadOnly)):
            raise TypeError('parent register must be of type reg_cls but got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle, msb=msb, lsb=lsb,
                         parent_register=parent_register, encoding_enum=encoding_enum)

    @Field.parent_register.getter
    def parent_register(self) -> readable_reg_type:
        assert isinstance(super().parent_register, (RegReadOnly, RegReadWrite))
        return super().parent_register

    def __reverse_enum_value_lookup(self, int_value: int):

        for potential_value in self.enum_cls:
            if int_value == potential_value.value:
                return potential_value
        else:
            raise('Unable to match value %d' % int_value)

    def read(self):
        int_value = (self.parent_register.read() & self.bitmask) >> self.lsb
        return self.__reverse_enum_value_lookup(int_value)


class EnumFieldReadWrite(EnumFieldReadOnly):

    __slots__ = []

    def __init__(self, parent_register: RegReadWrite, msb: int, lsb: int, encoding_enum, logger_handle: str):

        if not isinstance(parent_register, RegReadWrite):
            raise TypeError('parent register must be of type reg_cls but got %s' % type(parent_register))

        super().__init__(logger_handle=logger_handle, msb=msb, lsb=lsb, encoding_enum=encoding_enum,
                         parent_register=parent_register)

    @Field.parent_register.getter
    def parent_register(self) -> RegReadWrite:
        return super().parent_register

    def write(self, value):

        if not isinstance(value, self.enum_cls):
            raise TypeError('value must be an int but got %s' % type(value))

        if (self.msb == (self.parent_register.data_width - 1)) and (self.lsb == 0):
            # special case where the field occupies the whole register, there a straight write can be performed
            new_reg_value = value.value
        else:
            # do a read, modify write
            reg_value = self.parent_register.read()

            new_reg_value = (reg_value & self.inverse_bitmask) | (value.value << self.lsb)

        self.parent_register.write(new_reg_value)
