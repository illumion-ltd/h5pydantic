from hdf5popo import H5Group
import h5py

import pytest

def test_empty_hdf5(tmp_path):
    class EmptyHDF(H5Group):
        pass

    hdf5_filename = tmp_path / "empty.hdf"

    empty = EmptyHDF()

    empty.dump(hdf5_filename)

    with h5py.File(hdf5_filename, "r") as f:
        assert list(f.keys()) == []

def test_attribute(tmp_path):
    class AttributeHDF(H5Group):
        foo: str

    hdf5_filename = tmp_path / "empty.hdf"

    dp = AttributeHDF(foo="bar")

    dp.dump(hdf5_filename)

    with h5py.File(hdf5_filename, "r") as f:
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

    empty_input = EmptyHDF.load(hdf5_filename)

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

    print("exp_out", exp_out)

    exp_out.dump(hdf5_filename)

    exp_in = Experiment.load(hdf5_filename)

    assert exp_in == exp_out
    

# TODO test an attribute not defined
# TODO test setting a value of the wrong type
# TODO hypothesis testing load <-> dump
