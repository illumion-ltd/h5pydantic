from h5pydantic.types import H5Integer64

import h5py

import pytest

def test_integer_minimum_works(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        h5["/"].attrs["number"] = H5Integer64.ge


def test_outside_integer_minimum_fails(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        with pytest.raises(TypeError, match="has no native HDF5 equivalent"):
            h5["/"].attrs["number"] = H5Integer64.ge - 1


def test_integer_maximum_works(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        h5["/"].attrs["number"] = H5Integer64.le


def test_outside_integer_maximum_fails(tmp_path):

    h5_path = tmp_path / "test.pdf"

    with h5py.File(tmp_path / "test.hdf", 'w') as h5:
        with pytest.raises(TypeError, match="has no native HDF5 equivalent"):
            h5["/"].attrs["number"] = H5Integer64.le + 1
