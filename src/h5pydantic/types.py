from pydantic import StrictInt


class H5Type():
    """All subclasses must be able to save all their possible values to HDF5 without error."""


class H5Integer64(StrictInt, H5Type):
    """Signed Integers, using 64 bits."""

    ge = -2**63
    le = 2**64 - 1

