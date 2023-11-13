from h5pydantic.types import H5Int32, H5Int64, _hdfstrtoh5type, _pytype_to_h5type

import h5py

import pytest

def test_integer_minimum_works(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        h5["/"].attrs["number"] = H5Int64.ge


def test_outside_integer_minimum_fails(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        with pytest.raises(TypeError, match="has no native HDF5 equivalent"):
            h5["/"].attrs["number"] = H5Int64.ge - 1


def test_integer_maximum_works(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        h5["/"].attrs["number"] = H5Int64.le


def test_outside_integer_maximum_fails(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        with pytest.raises(TypeError, match="has no native HDF5 equivalent"):
            h5["/"].attrs["number"] = H5Int64.le + 1

def test_unknown_hdf_data_type_fails():
    with pytest.raises(ValueError, match="nosuchtype"):
        _hdfstrtoh5type("nosuchtype")

@pytest.mark.parametrize("pytype,h5type",
                         [(H5Int32, h5py.h5t.NATIVE_INT32),
                          (H5Int64, h5py.h5t.NATIVE_INT64),
                          (str, None),
                          (float, float)])
def test_known_types(pytype, h5type):
    h5 = _pytype_to_h5type(pytype)

    assert h5type == h5


def test_unknown_pytypes():
    with pytest.raises(ValueError):
        _pytype_to_h5type(tuple)
