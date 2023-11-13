import h5py
from pydantic import BaseModel, PrivateAttr, StrictInt

import numpy

from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath
from enum import Enum
import types

from typing import get_args, get_origin
from typing import Any, Union
from typing_extensions import Self, Type

from .enum import H5Enum
from .types import H5Type, _hdfstrtoh5type, _pytype_to_h5type

_H5Container = Union[h5py.Group, h5py.Dataset]

# FIXME strings probably need some form of validation, printable seems good, but may be too strict

class _H5Base(BaseModel):
    """An implementation detail, to share the _load and _dump APIs."""

    def __init_subclass__(self, **data: Any):
        for key, field in self.__fields__.items():
            if isinstance(field.outer_type_, types.GenericAlias):

                if get_origin(field.outer_type_) != list:
                    raise ValueError(f"h5pydantic only handles list containers, not '{get_origin(field.outer_type_)}'")

                if issubclass(field.type_, Enum):
                    raise ValueError(f"h5pydantic does not handle lists of enums")

    @abstractmethod
    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> _H5Container:
        """Dump the group/dataset container to the h5file."""

    def _dump_children(self, container: _H5Container, h5file: h5py.File, prefix: PurePosixPath):
        for key, field in self.__fields__.items():
            # FIXME I think I should be explicitly testing these keys against a known list, at init time though.
            # FIXME I really don't like this delegation code.
            value = getattr(self, key)
            if get_origin(field.outer_type_) is list:
                for i, elem in enumerate(value):
                    elem._dump(h5file, prefix / key / str(i))
            elif issubclass(field.type_, Enum):
                H5Enum._dump(h5file, container, key, value.value, field)

            elif isinstance(value, _H5Base):
                value._dump(h5file, prefix / key)

            else:
                # FIXME should handle shape here. (i.e. datasets)
                dtype=_pytype_to_h5type(field.type_)
                # FIXME set the type explicitly
                container.attrs.create(key, getattr(self, key)) #  dtype=_pytype_to_h5type(field.type_))

    def _dump(self, h5file: h5py.File, prefix: PurePosixPath) -> None:
        container = self._dump_container(h5file, prefix)
        self._dump_children(container, h5file, prefix)

    @classmethod
    def _load_intrinsic(cls, h5file: h5py.File, prefix: PurePosixPath) -> dict:
        return {}

    @classmethod
    def _load_children(cls, h5file: h5py.File, prefix: PurePosixPath):
        # FIXME specialise away Any
        d: dict[str, Any] = {}
        for key, field in cls.__fields__.items():
            if isinstance(field.outer_type_, types.GenericAlias):
                d[key] = []
                indexes = [int(i) for i in h5file[str(prefix / key)].keys()]
                indexes.sort()
                for i in indexes:
                    # FIXME This doesn't check a lot of cases.
                    d[key].insert(i, field.type_._load(h5file, prefix / key / str(i)))
            elif issubclass(field.type_, _H5Base):
                d[key] = field.type_._load(h5file, prefix / key)

            elif issubclass(field.type_, Enum):
                d[key] = H5Enum._load(h5file, prefix, key, field)

            else:
                d[key] = h5file[str(prefix)].attrs[key]

        return d

    @classmethod
    def _load(cls, h5file: h5py.File, prefix: PurePosixPath) -> Self:
        d = cls._load_intrinsic(h5file, prefix)
        d.update(cls._load_children(h5file, prefix))
        ret = cls.parse_obj(d)

        # FIXME awful hack, _data isn't being loaded by parse_obj for some reason
        if "_data" in d:
            ret._data = d["_data"]

        return ret


class H5DatasetConfig(BaseModel):
    """All of the dataset configuration options."""
    # FIXME There are a *lot* of dataset features to be supported as optional flags, compression, chunking etc.
    shape: tuple[StrictInt, ...]
    dtype: Union[Type[str],Type[float],Type[H5Type],Type[Enum]]


class H5Dataset(_H5Base):
    """A pydantic Basemodel specifying a HDF5 Dataset."""

    _h5config: H5DatasetConfig = PrivateAttr()
    _data: numpy.ndarray = PrivateAttr()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        cls._h5config = H5DatasetConfig(**kwargs)

    class Config:
        # Allows numpy.ndarray (which doesn't have a validator).
        arbitrary_types_allowed = True

    # FIXME test for attributes on datasets

    def data(self, data: numpy.ndarray):
        """Set the data of the dataset.

        The expectation is that the dataset will be created as a whole, then set using this method.
        """
        # FIXME check shape and datatype are compatible, tests for that.
        self._data = data

    def _dtype(self) -> H5Type:
        if issubclass(self._h5config.dtype, Enum):
            return self._h5config.dtype.dtype()
        else:
            return self._h5config.dtype

    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> h5py.Dataset:
        # FIXME check that the shape of data matches
        # FIXME add in all the other flags
        dataset = h5file.require_dataset(str(prefix), shape=self._h5config.shape,
                                         dtype=_pytype_to_h5type(self._dtype()),
                                         data=self._data)
        return dataset

    @classmethod
    def _load_intrinsic(cls, h5file: h5py.File, prefix: PurePosixPath) -> dict:
        # Really should be verifying all of the details match the class.
        data = h5file[str(prefix)][()]
        return {"_config": H5DatasetConfig(shape=data.shape, dtype=_hdfstrtoh5type(data.dtype)), "_data": data}

    def __eq__(self, other):
        intrinsic = numpy.array_equal(self._data, other._data)
        children = all([getattr(self, k) == getattr(other, k) for k in self.__fields__])
        return intrinsic and children


class H5Group(_H5Base):
    """A pydantic BaseModel specifying a HDF5 Group."""

    _h5file: h5py.File = PrivateAttr()

    @classmethod
    def load(cls, filename: Path) -> Self:
        """Load a file into a tree of H5Group models.

        Args:
            filename: Path of HDF5 to load.

        Returns:
            The parsed H5Group model.
        """
        h5file = h5py.File(filename, "r")
        # TODO actually build up the list of unparsed keys
        group = cls._load(h5file, PurePosixPath("/"))
        group._h5file = h5file
        return group

    def close(self):
        """Close the underlying HDF5 file.
        """
        self._h5file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> h5py.Group:
        return h5file.require_group(str(prefix))

    def dump(self, filename: Path):
        """Dump the H5Group object tree into a file.

        Args:
            filename: Path to dump the the HDF5Group to.

        Returns: None
        """
        with h5py.File(filename, "w") as h5file:
            self._dump(h5file, PurePosixPath("/"))

    def __eq__(self, other):
        return all([getattr(self, k) == getattr(other, k) for k in self.__fields__])
