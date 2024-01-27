from h5pydantic import H5Group, H5Dataset, H5Int64

import numpy

import pytest


def test_shape_ints_are_strictly_ints():
    with pytest.raises(ValueError, match="value is not a valid integer"):
        class FloatShape(H5Dataset, shape=(1.0, 2.0), dtype=H5Int64):
            pass

# FIXME check for strict ints in dataset shape tuples, don't accept floats
# FIXME check data types in assinment, correct dtype for arrays, strictstr for string

def test_initialised_datasets_are_immutable():
    class Data(H5Dataset, shape=(2, 2), dtype=H5Int64):
        pass

    data = Data(data_=numpy.array([[1, 2], [3, 4]]))

    with pytest.raises(ValueError, match="Cannot modify dataset"):
        data[0, 0] = 3


def test_read_from_init_data(hdf_path):
    class Data(H5Dataset, shape=(2, 2), dtype=H5Int64):
        pass

    class Experiment(H5Group):
        data = Data()

    array_data = numpy.array([[1, 2], [3, 4]])

    exp = Experiment(data=Data(data_=array_data))

    numpy.array_equal(exp.data[()], array_data)


def test_scalar_str_dataset_dump(hdf_path):
    class ScalarData(H5Dataset, shape=(), dtype=str):
        pass

    class Experiment(H5Group):
        data = ScalarData()

    exp = Experiment(data=ScalarData(data_="foobarbazbarry"))

    exp.dump(hdf_path)

    with Experiment.load(hdf_path) as loaded:
        assert loaded.data[()] == "foobarbazbarry"


def test_scalar_str_dataset_dumper(hdf_path):
    class ScalarData(H5Dataset, shape=(), dtype=str):
        pass

    class Experiment(H5Group):
        data = ScalarData()

    exp = Experiment()

    with exp.dumper(hdf_path):
        exp.data[()] = "foobarbaz"

    with Experiment.load(hdf_path) as loaded:
        assert loaded.data[()] == "foobarbaz"
