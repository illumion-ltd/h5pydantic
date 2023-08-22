from h5pydantic import H5Group, H5Dataset, H5Integer32
import h5py

import numpy as np

import pytest

def test_empty_hdf5(tmp_path):
    class EmptyHDF(H5Group):
        pass

    hdf5_filename = tmp_path / "empty.hdf"

    empty = EmptyHDF()

    empty.dump(hdf5_filename)

    with h5py.File(hdf5_filename, "r") as f:
        assert list(f.keys()) == []

def test_attribute(hdf_path):
    print("hdf_path", hdf_path)

    class AttributeHDF(H5Group):
        foo: str

    dp = AttributeHDF(foo="bar")

    dp.dump(hdf_path)

    with h5py.File(hdf_path, "r") as f:
        assert list(f.keys()) == []
        assert list(f.attrs.keys()) == ["foo"]
        assert f.attrs["foo"] == "bar"

def test_missing_attribute(tmp_path):
    class AttributeHDF(H5Group):
        foo: str

    dp = AttributeHDF(foo="bar")

    with pytest.raises(ValueError):
        dp.baz = "no such attribute"


def test_empty_roundtrip(tmp_path):
    class EmptyHDF(H5Group):
        pass

    hdf5_filename = tmp_path / "empty.hdf"

    empty_output = EmptyHDF()

    empty_output.dump(hdf5_filename)

    with EmptyHDF.load(hdf5_filename) as empty_input:
        assert empty_output == empty_input


def test_nested(tmp_path):
    class Baseline(H5Group):
        temp1: float
        temp2: float

    class Experiment(H5Group):
        before: Baseline
        after: Baseline

    hdf5_filename = tmp_path / "nested.hdf"

    exp_out = Experiment(before=Baseline(temp1=10.0, temp2=11.0),
                         after=Baseline(temp1=21.0, temp2=22.0))

    exp_out.dump(hdf5_filename)

    with Experiment.load(hdf5_filename) as exp_in:
        assert exp_in == exp_out


def test_enumerate(tmp_path):
    class Reading(H5Group):
        temp: float
        humidity: float

    class Experiment(H5Group):
        readings: list[Reading]

    hdf5_filename = tmp_path / "enumerate.hdf"

    exp_out = Experiment(readings=[{"temp": 20.0, "humidity": 0.45},
                                   {"temp": 30.0, "humidity": 0.5}])

    exp_out.dump(hdf5_filename)

    with Experiment.load(hdf5_filename) as exp_in:
        assert exp_in == exp_out


def test_dataset(hdf_path):
    IMAGE_SHAPE = (3, 5)

    class AreaDetectorImage(H5Dataset, shape=IMAGE_SHAPE, dtype=H5Integer32):
        pass

    class Experiment(H5Group):
        image = AreaDetectorImage()

    exp_out = Experiment()

    exp_out.image.data(np.random.randint(256, size=IMAGE_SHAPE))

    exp_out.dump(hdf_path)

    with Experiment.load(hdf_path) as exp_in:
        assert exp_in == exp_out

# TODO test an attribute not defined
# TODO test setting a value of the wrong type
# TODO hypothesis testing load <-> dump
# TODO data set labels, check that len(lables) == len(shape)
