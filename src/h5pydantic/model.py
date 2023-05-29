import h5py
from pydantic import BaseModel
import numpy

from abc import ABC, abstractmethod
from pathlib import Path, PurePosixPath
import types

from typing import Any, Union

_H5Container = Union[h5py.Group, h5py.Dataset]


class _H5Base(ABC, BaseModel):
    """An implementation detail, to share the _load and _dump APIs."""

    def __init__(self, **data: Any):
        super().__init__(**data)
        for key, field in self.__fields__.items():
            if key.endswith("_"):
                continue

            if isinstance(field.outer_type_, types.GenericAlias):
                # FIXME clearly I should not be looking at these attributes.
                if not issubclass(field.outer_type_.__origin__, list):
                    raise ValueError(f"h5pydantic only handles list containers, not '{field.outer_type_.__origin__}'")

    @abstractmethod
    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> _H5Container:
        """Dump the group/dataset container to the h5file."""

    def _dump_children(self, container: _H5Container, h5file: h5py.File, prefix: PurePosixPath):
        for key, field in self.__fields__.items():
            # FIXME I think I should be explicitly testing these keys against a known list, at init time though.
            if key.endswith("_"):
                continue
            value = getattr(self, key)
            if isinstance(value, _H5Base):
                value._dump(h5file, prefix / key)
            elif isinstance(value, list):
                for i, elem in enumerate(value):
                    elem._dump(h5file, prefix / key / str(i))
            else:
                container.attrs[key] = getattr(self, key)

    def _dump(self, h5file: h5py.File, prefix: PurePosixPath) -> None:
        container = self._dump_container(h5file, prefix)
        self._dump_children(container, h5file, prefix)

    @classmethod
    def _load_intrinsic(cls, h5file: h5py.File, prefix: PurePosixPath) -> dict:
        return {}

    @classmethod
    def _load_children(cls, h5file: h5py.File, prefix: PurePosixPath):
        d = {}
        for key, field in cls.__fields__.items():
            if key.endswith("_"):
                continue

            if isinstance(field.outer_type_, types.GenericAlias):
                d[key] = []
                indexes = [int(i) for i in h5file[str(prefix / key)].keys()]
                indexes.sort()
                for i in indexes:
                    # FIXME This doesn't check a lot of cases.
                    d[key].insert(i, field.type_._load(h5file, prefix / key / str(i)))
            elif issubclass(field.type_, _H5Base):
                d[key] = field.type_._load(h5file, prefix / key)
            else:
                d[key] = h5file[str(prefix)].attrs[key]

        return d

    @classmethod
    def _load(cls, h5file: h5py.File, prefix: PurePosixPath) -> tuple["H5Group", list[str]]:
        d = cls._load_intrinsic(h5file, prefix)
        d.update(cls._load_children(h5file, prefix))
        return cls.parse_obj(d)


class H5Dataset(_H5Base):
    """A pydantic Basemodel specifying a HDF5 Dataset."""

    class Config:
        # Allows numpy.ndarray (which doesn't have a validator).
        arbitrary_types_allowed = True

    # FIXME check that all underscore attributes are special attributes

    # FIXME refactor _load/_dump apis
    # There are a *lot* of dataset features to be supported as optional flags, compression, chunking etc.
    # FIXME test for attributes on datasets
    # FIXME I'm not comfortable with shadowing these fields like this,
    # but it's nice to have some ns to put config variables in.
    shape_: tuple[int, ...]
    dtype_: str = "f"

    # FIXME is it possible to initialise this after we've got shape_ and dtype_ in the instance?
    data_: Union[h5py.Dataset, numpy.ndarray] = None

    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> h5py.Dataset:
        # FIXME check that the shape of data matches
        # FIXME add in all the other flags
        dataset = h5file.require_dataset(str(prefix), shape=self.shape_, dtype=self.dtype_)
        dataset[:] = self.data_
        return dataset

    @classmethod
    def _load_intrinsic(cls: BaseModel, h5file: h5py.File, prefix: PurePosixPath):
        # Really should be verifying all of the details match the class.
        data = h5file[str(prefix)][()]
        return {"shape_": data.shape, "dtype_": str(data.dtype), "data_": data}

    def __eq__(self, other):
        intrinsic = numpy.array_equal(self.data_, other.data_)
        children = all([getattr(self, k) == getattr(other, k) for k in self.__fields__ if not k.endswith("_")])
        return intrinsic and children


class H5Group(_H5Base):
    """A pydantic BaseModel specifying a HDF5 Group."""

    class Config:
        # For the _h5file attribute.
        underscore_attrs_are_private = True

    _h5file: h5py.File = None

    @classmethod
    def load(cls: BaseModel, filename: Path) -> "H5Group":
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
        return all([getattr(self, k) == getattr(other, k) for k in self.__fields__ if not k.endswith("_")])
