"""
This package is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of classes used by the autogenerated code
"""

from .callbacks import ReadCallback
from .callbacks import ReadBlockCallback
from .callbacks import WriteCallback
from .callbacks import WriteBlockCallback
from .callbacks import NormalCallbackSet
from .callbacks import AsyncCallbackSet
from .callbacks import CallbackSet

from .base import AddressMap
from .base import RegFile
from .base import AddressMapArray
from .base import RegFileArray

from .register import Reg
from .register import RegisterWriteVerifyError

from .register import RegReadOnly
from .register import RegWriteOnly
from .register import RegReadWrite
from .register import WritableRegister
from .register import ReadableRegister

from .register import RegReadOnlyArray
from .register import RegWriteOnlyArray
from .register import RegReadWriteArray
from .register import ReadableRegisterArray
from .register import WritableRegisterArray


from .register import RegAsyncReadOnly
from .register import RegAsyncWriteOnly
from .register import RegAsyncReadWrite
from .register import ReadableAsyncRegister
from .register import WritableAsyncRegister
from .register import RegAsyncReadOnlyArray
from .register import RegAsyncWriteOnlyArray
from .register import RegAsyncReadWriteArray
from .register import ReadableAsyncRegisterArray
from .register import WritableAsyncRegisterArray

from .fields import FieldSizeProps
from .fields import FieldMiscProps
from .fields import FieldReadOnly
from .fields import FieldWriteOnly
from .fields import FieldReadWrite
from .fields import Field
from .fields import FieldEnumReadOnly
from .fields import FieldEnumWriteOnly
from .fields import FieldEnumReadWrite
from .fields import FieldEnum

from .fields import FieldAsyncReadOnly
from .fields import FieldAsyncWriteOnly
from .fields import FieldAsyncReadWrite
from .fields import FieldEnumAsyncReadOnly
from .fields import FieldEnumAsyncWriteOnly
from .fields import FieldEnumAsyncReadWrite

from .memory import Memory
from .memory import MemoryReadOnly
from .memory import MemoryWriteOnly
from .memory import MemoryReadWrite
from .memory import MemoryReadOnlyArray
from .memory import MemoryWriteOnlyArray
from .memory import MemoryReadWriteArray
from .memory import MemoryAsyncReadOnly
from .memory import MemoryAsyncWriteOnly
from .memory import MemoryAsyncReadWrite
from .memory import MemoryAsyncReadOnlyArray
from .memory import MemoryAsyncWriteOnlyArray
from .memory import MemoryAsyncReadWriteArray

from .base import get_array_typecode
