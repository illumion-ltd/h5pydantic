from pydantic import StrictInt

from enum import Enum

import h5py.h5t

import numpy

from typing import Union, Type


class H5Type():
    """All subclasses must be able to save all their possible values to HDF5 without error."""

    numpy: Type[numpy.number]
    h5pyid: h5py.h5t.TypeIntegerID

# FIXME add other types, add tests for ge/le for them as well.
# FIXME add a validator, for ints not to accept float


class H5Int64(int, H5Type):
    """Signed Integers, using 64 bits."""

    ge = -2**63
    le = 2**64 - 1
    h5pyid = h5py.h5t.NATIVE_INT64
    numpy = numpy.int64


class H5Int32(int, H5Type):
    """Signed Integers, using 32 bits."""

    ge = -2**31
    le = 2**31 - 1
    h5pyid = h5py.h5t.NATIVE_INT32
    numpy = numpy.int32


def _pytype_to_h5type(pytype: Union[Type[H5Type],Type[str],Type[float]]) -> Union[Type[str],Type[float],Type[numpy.dtype],None]:
    """Map from the Python type to the h5py type."""
    if issubclass(pytype, H5Type):
        return pytype.h5pyid

    elif pytype is str:
        return h5py.string_dtype(encoding="utf8", length=None)

    elif pytype in [float]:
        return pytype

    elif issubclass(pytype, Enum):
        return _pytype_to_h5type(pytype.__h5dtype__)

    else:
        raise ValueError(f"Unknown type: {pytype}")
