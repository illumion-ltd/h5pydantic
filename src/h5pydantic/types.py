from pydantic import StrictInt, StrictStr
from enum import Enum
import h5py.h5t
import numpy
from typing import Union, Type


CHECK_CASTABLE = [h5py.h5t.STRING, h5py.h5t.NATIVE_B8, h5py.h5t.COMPOUND]

class H5Type():
    """All subclasses must be able to save all their possible values to HDF5 without error."""

    numpy: Type[numpy.number]
    h5pyid: h5py.h5t.TypeIntegerID

# FIXME add other types, add tests for ge/le for them as well.
# FIXME add a validator, for ints not to accept float


class H5Int64(int, H5Type):
    """Signed Integers, using 64 bits."""

    ge = -2**63
    le = 2**63 - 1
    h5pyid = h5py.h5t.NATIVE_INT64
    numpy = numpy.int64


class H5Int32(int, H5Type):
    """Signed Integers, using 32 bits."""

    ge = -2**31
    le = 2**31 - 1
    h5pyid = h5py.h5t.NATIVE_INT32
    numpy = numpy.int32

class H5Int8(int, H5Type):
    """Unsigned Integers, using 16 bits."""

    ge = -2**7
    le = 2**7 - 1
    h5pyid = h5py.h5t.NATIVE_INT8
    numpy = numpy.int8

class H5UInt16(int, H5Type):
    """Unsigned Integers, using 16 bits."""

    ge = 0
    le = 2**16 - 1
    h5pyid = h5py.h5t.NATIVE_UINT16
    numpy = numpy.uint16

class H5UInt32(int, H5Type):
    """Unsigned Integers, using 32 bits."""

    ge = 0
    le = 2**32 - 1
    h5pyid = h5py.h5t.NATIVE_UINT32
    numpy = numpy.uint32

class H5Float32(float, H5Type):
    """Little Endian float, using 32 bits."""

    ge = numpy.finfo(numpy.float32).min
    le = numpy.finfo(numpy.float32).max
    h5pyid = h5py.h5t.IEEE_F32LE
    numpy = numpy.float32


class H5Float64(float, H5Type):
    """Little Endian float, using 64 bits."""

    ge = numpy.finfo(numpy.float64).min
    le = numpy.finfo(numpy.float64).max
    h5pyid = h5py.h5t.FLOAT
    numpy = numpy.float64

class H5String(str, H5Type):
    """String"""

    h5pyid = h5py.h5t.STRING
    numpy = numpy.object_


class H5Bool(int, H5Type):
    """Unsigned Integers, using 8 bits."""

    ge = 0
    le = 2**8 - 1
    h5pyid = h5py.h5t.NATIVE_B8
    numpy = numpy.bool_

class H5List(list, H5Type):

    h5pyid = h5py.h5t.ARRAY
    numpy = numpy.s_

class H5Compound(H5Type):

    h5pyid = h5py.h5t.COMPOUND
    numpy = numpy.dtypes.VoidDType 


def _pytype_to_h5type(pytype: Union[Type[Enum],Type[H5Type],Type[str],Type[float]], use_np:bool = True) -> Union[Type[Enum],Type[H5Type],Type[str],Type[float]]:
    """Map from the Python type to the h5py type."""
    if issubclass(pytype, H5Type):
        if use_np:
            return pytype.numpy
        else:
            return pytype.h5pyid

    elif pytype in [str, StrictStr]:
        return h5py.string_dtype(encoding="utf8", length=None)

    elif pytype in [float]:
        return pytype

    else:
        raise ValueError(f"Unknown type: {pytype}")
