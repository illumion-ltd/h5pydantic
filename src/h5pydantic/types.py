from pydantic import StrictInt

import h5py.h5t


class H5Type():
    """All subclasses must be able to save all their possible values to HDF5 without error."""


# FIXME, add other types, add tests for ge/le for them as well.

class H5Integer64(StrictInt, H5Type):
    """Signed Integers, using 64 bits."""

    ge = -2**63
    le = 2**64 - 1
    h5pyid = h5py.h5t.NATIVE_INT64
