from pydantic import StrictInt

import h5py.h5t

import numpy


class H5Type():
    """All subclasses must be able to save all their possible values to HDF5 without error."""


# FIXME add other types, add tests for ge/le for them as well.
# FIXME add a validator, for ints not to accept float

class H5Integer64(int, H5Type):
    """Signed Integers, using 64 bits."""

    ge = -2**63
    le = 2**64 - 1
    h5pyid = h5py.h5t.NATIVE_INT64
    numpy = numpy.int64


class H5Integer32(int, H5Type):
    """Signed Integers, using 32 bits."""

    ge = -2**31
    le = 2**31 - 1
    h5pyid = h5py.h5t.NATIVE_INT32
    numpy = numpy.int32


def _pytype_to_h5type(pytype: H5Type|str|float) -> str:
    """Maps from the Python type to the h5py type."""
    if issubclass(pytype, H5Type):
        return pytype.h5pyid

    elif pytype is str:
        return numpy.dtype("str")

    elif pytype in [float]:
        return pytype

    else:
        raise ValueError(f"Unknown type: {pytype}")


def _hdfstrtoh5type(hdfdtype: str) -> H5Type|float:
    # FIXME this should be a registered look up table or something more automatic
    if hdfdtype == "int32":
        return H5Integer32
    elif hdfdtype == "int64":
        return H5Integer64
    else:
        raise ValueError(f"Unknown hdf5 data dtype string '{hdfdtype}'")
