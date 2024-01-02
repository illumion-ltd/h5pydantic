from h5pydantic import H5Dataset, H5Group, H5Int64

import numpy as np

from enum import IntEnum

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
# FIXME can we make a dataset of enums?
# FIXME test that all values fit inside the base datatype
# FIXME test that the loaded underlying datatype is the same as that written out


class ScanningMode(IntEnum):
    __h5dtype__ = H5Int64
    INSTANTANEOUS = 1
    STEPANDSHOOT = 2
    FLYSCAN = 3


@pytest.mark.parametrize("mode", ScanningMode.__members__.values())
def test_enum_works(hdf_path, mode):
    class Experiment(H5Group):
        mode: ScanningMode

    exp = Experiment(mode=mode)

    exp.dump(hdf_path)

    with Experiment.load(hdf_path) as imported:
        assert exp == imported


def test_list_enum_fails(hdf_path):
    with pytest.raises(ValueError, match="h5pydantic does not handle lists of enums"):
        class Experiment(H5Group):
            modes: list[ScanningMode]


def test_dataset_enum_works(hdf_path):
    class DatasetModes(H5Dataset, shape=(3,), dtype=ScanningMode):
        pass

    class Experiment(H5Group):
        modes = DatasetModes()

    modes_array = np.array([ScanningMode.INSTANTANEOUS, ScanningMode.STEPANDSHOOT, ScanningMode.FLYSCAN])
    exp = Experiment(modes=DatasetModes(data_=modes_array))
    exp.dump(hdf_path)

    with Experiment.load(hdf_path) as loaded:
        assert exp == loaded
        assert np.array_equal(modes_array, loaded.modes[()])
