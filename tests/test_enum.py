from h5pydantic import H5Group, H5Integer64

from enum import IntEnum, unique

import pytest

# FIXME make sure the base type of the enum is exactly one of our hdf5 int types
# FIXME make sure that only integer values are defined
# FIXME make sure the enum is python integer type
# FIXME make sure that the enum is @unique flagged
# FIXME make sure that the enum is @continuous flagged
# FIXME make sure all the elements are integers
# FIXME check what happens with a negative number
# FIXME check what happens with an out of sequence number
# FIXME test using the same enum twice in one hdf5 file
# FIXME can we make a list of enums?
# FIXME can we make a dataset of enums?
# FIXME test that all values fit inside the base datatype

class ScanningMode(IntEnum):
    INSTANTANEOUS = 1
    STEPANDSHOOT = 2
    FLYSCAN = 3

    @classmethod
    def h5dtype(cls):
        return H5Integer64

@pytest.mark.parametrize("mode", ScanningMode.__members__.values())
def test_enum_works(hdf_path, mode):
    class Experiment(H5Group):
        mode: ScanningMode

    exp = Experiment(mode=mode)

    exp.dump(hdf_path)

    with Experiment.load(hdf_path) as imported:
        assert exp == imported

    
