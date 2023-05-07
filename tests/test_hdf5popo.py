from hdf5popo import HDF5DataProduct
import h5py

import pytest

def test_empty_hdf5(tmp_path):
    class EmptyHDF(HDF5DataProduct):
        pass

    hdf5_filename = tmp_path / "empty.hdf"

    empty = EmptyHDF()

    empty.dump(hdf5_filename)

    with h5py.File(hdf5_filename, "r") as f:
        assert list(f.keys()) == []

def test_attribute(tmp_path):
    class AttributeHDF(HDF5DataProduct):
        foo: str

    hdf5_filename = tmp_path / "empty.hdf"

    dp = AttributeHDF(foo="bar")

    dp.dump(hdf5_filename)

    with h5py.File(hdf5_filename, "r") as f:
        assert list(f.keys()) == []
        assert list(f.attrs.keys()) == ["foo"]
        assert f.attrs["foo"] == "bar"

def test_missing_attribute(tmp_path):
    class AttributeHDF(HDF5DataProduct):
        foo: str

    dp = AttributeHDF(foo="bar")

    with pytest.raises(ValueError):
        dp.baz = "no such attribute"

def test_empty_roundtrip(tmp_path):
    class EmptyHDF(HDF5DataProduct):
        pass

    hdf5_filename = tmp_path / "empty.hdf"

    empty_output = EmptyHDF()

    empty_output.dump(hdf5_filename)

    empty_input = EmptyHDF.load(hdf5_filename)

    assert empty_output == empty_input
    

# TODO test an attribute not defined
# TODO test setting a value of the wrong type
# TODO hypothesis testing load <-> dump
