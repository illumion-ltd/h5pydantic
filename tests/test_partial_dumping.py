from h5pydantic import H5Group, H5Dataset, H5Int32, H5PartialDump

from typing import Optional

import pytest

import numpy


class Data(H5Dataset, shape=(2, 2), dtype=H5Int32):
    pass


class Experiment(H5Group):
    optData: Optional[Data] = None
    manData: Data = Data()


def test_partial_dump_works(hdf_path):
    exp = Experiment()

    exp.dump(hdf_path, partial=True)


def test_partial_dump_complains(hdf_path):
    exp = Experiment()

    with pytest.raises(H5PartialDump) as excinfo:
        exp.dump(hdf_path)

    assert excinfo.value.datasets == ["Experiment.manData"]


def test_partial_dumper_works(hdf_path):
    exp = Experiment()

    with exp.dumper(hdf_path, partial=True):
        pass


def test_partial_dumper_complains(hdf_path):
    exp = Experiment()

    with pytest.raises(H5PartialDump) as excinfo:
        with exp.dumper(hdf_path):
            pass

    assert excinfo.value.datasets == ["Experiment.manData"]

# test dump with list of datasets
# test dumper with list of datasets
