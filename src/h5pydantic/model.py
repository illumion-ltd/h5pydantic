import h5py
from pydantic import BaseModel, PrivateAttr, StrictInt, StrictStr

import numpy

from abc import abstractmethod
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from enum import Enum
import types

from typing import get_origin
from typing import Any, Optional, Union
from typing_extensions import Self, Type

from .enum import _h5enum_dump, _h5enum_load
from .exceptions import H5PartialDump
from .types import H5Type, _pytype_to_h5type

_H5Container = Union[h5py.Group, h5py.Dataset]

# FIXME strings probably need some form of validation, printable seems good, but may be too strict


class _H5Base(BaseModel):
    """An implementation detail, to share the _load and _dump APIs."""

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for key, field in cls.__fields__.items():
            if isinstance(field.outer_type_, types.GenericAlias):

                if get_origin(field.outer_type_) != list:
                    raise TypeError(f"h5pydantic only handles list containers, not '{get_origin(field.outer_type_)}'")

                if issubclass(field.type_, Enum):
                    raise TypeError("h5pydantic does not handle lists of enums")

            elif field.type_ is str:
                # FIXME this is an awful way of coercing a type, not sure what the right thing to do is.
                field.type_ = StrictStr
                field.populate_validators()

    @abstractmethod
    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> _H5Container:
        """Dump the group/dataset container to the h5file."""

    def _dump_children(self, container: _H5Container, h5file: h5py.File, prefix: PurePosixPath):
        for key, field in self.__fields__.items():
            # FIXME I think I should be explicitly testing these keys against a known list, at init time though.
            # FIXME I really don't like this delegation code.
            value = getattr(self, key)
            if field.required is False and value is None:
                continue

            elif get_origin(field.outer_type_) is list:
                for i, elem in enumerate(value):
                    elem._dump(h5file, prefix / key / str(i))
            elif isinstance(value, Enum):
                _h5enum_dump(h5file, container, key, value.value, field)

            elif isinstance(value, _H5Base):
                value._dump(h5file, prefix / key)

            else:
                # FIXME should handle shape here. (i.e. datasets)
                dtype = _pytype_to_h5type(field.type_)
                # FIXME set the type explicitly
                container.attrs.create(key, getattr(self, key)) #  dtype=_pytype_to_h5type(field.type_))

    def _dump(self, h5file: h5py.File, prefix: PurePosixPath):
        container = self._dump_container(h5file, prefix)
        self._dump_children(container, h5file, prefix)

    @classmethod
    def _load_intrinsic(cls, h5file: h5py.File, prefix: PurePosixPath) -> dict[str, Any]:
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
                if field.required is False and str(prefix / key) not in h5file:
                    d[key] = None
                else:
                    d[key] = field.type_._load(h5file, prefix / key)

            elif issubclass(field.type_, Enum):
                d[key] = _h5enum_load(h5file, prefix, key, field)

            else:
                if field.required is False and key not in h5file[str(prefix)].attrs:
                    d[key] = None
                else:
                    d[key] = h5file[str(prefix)].attrs[key]

        return d

    @classmethod
    def _load(cls, h5file: h5py.File, prefix: PurePosixPath) -> Self:
        d = cls._load_intrinsic(h5file, prefix)
        d.update(cls._load_children(h5file, prefix))
        return cls(**d)

class H5DatasetConfig(BaseModel):
    """All of the dataset configuration options."""
    # FIXME There are a *lot* of dataset features to be supported as optional flags, compression, chunking etc.
    shape: tuple[StrictInt, ...]
    dtype: Union[Type[str],Type[float],Type[H5Type],Type[Enum]]


class H5Dataset(_H5Base):
    """A :class:`pydantic.BaseModel` representing a :class:`h5py.Dataset`.
    """

    _h5config: H5DatasetConfig = PrivateAttr()
    _data: Optional[numpy.ndarray] = PrivateAttr(default=None)
    _dset: Optional[h5py.Dataset] = PrivateAttr(default=None)
    _modified: bool = PrivateAttr(default=False)


    @classmethod
    def __init_subclass__(cls, **kwargs):
        cls._h5config = H5DatasetConfig(**kwargs)

    def __init__(self, data_: Optional[numpy.ndarray] = None, **kwargs):
        """
        Args:
            data_: allows the value of the DataSet to be initialised to a numpy.Array.
                   If this keyword is used, the data cannot be subsequently modified
                   using the array assignment syntax.
        """
        super().__init__(**kwargs)
        self._data = data_
        self._dset = kwargs.get("_dset", None)

    class Config:
        # Allows numpy.ndarray (which doesn't have a validator).
        arbitrary_types_allowed = True

    # FIXME test for attributes on datasets

    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> Self:
        # FIXME check that the shape of data matches
        # FIXME add in all the other flags
        self._dset = h5file.require_dataset(str(prefix), shape=self._h5config.shape,
                                            dtype=_pytype_to_h5type(self._h5config.dtype),
                                            data=self._data)
        self._modified = self._data is not None
        return self._dset

    @classmethod
    def _load_intrinsic(cls, h5file: h5py.File, prefix: PurePosixPath) -> dict:
        # FIXME Really should be verifying all of the details match the class.
        # FIXME should probably be doing exact=True here, but need to test what happens
        dset = h5file.require_dataset(str(prefix), cls._h5config.shape, _pytype_to_h5type(cls._h5config.dtype))
        return {"_dset": dset}

    def __getitem__(self, key):
        """Allow array like access to the underlying h5py Dataset.

        :meta public:
        """
        if self._dset:
            value = self._dset.__getitem__(key)

            if isinstance(value, bytes) and self._h5config.dtype is str:
                return value.decode()
            else:
                return value

        else:
            return self._data.__getitem__(key)

    def __setitem__(self, index, value):
        """Allow aray like assignment to the underlying h5py Datset.

        :meta public:
        """
        if self._data is not None:
            raise ValueError("Cannot modify data_ values given at __init__().")
        self._dset.__setitem__(index, value)
        self._modified = True

    # FIXME __len__?


class H5Group(_H5Base):
    """A :class:`pydantic.BaseModel` representing a :class:`h5py.Group`.

    This should be extended to model all your groups.
    """

    _h5file: h5py.File = PrivateAttr()

    class Config:
        validate_assignment = True

    @classmethod
    def load(cls, filename: Path) -> Self:
        """Load a file into a tree of H5Group models.

        Can be used as context manager, which allows dataset access in
        the body of the context manager, and will :meth:`close` the
        ``filename`` at the end of the context block.

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

    def _datasets(self, parent: str):
        for key, field in self.__fields__.items():
            value = getattr(self, key)

            # FIXME list of datasets

            if isinstance(value, H5Dataset):
                yield (parent + '.' + key, getattr(self, key))
            elif isinstance(value, H5Group):
                yield from getattr(self, key)._datasets(parent + '.' + key)

    def _check_all_modified(self):
        unset = []
        for (name, dataset) in self._datasets(self.__class__.__name__):
            if not dataset._modified:
                unset.append(name)

        if unset:
            raise H5PartialDump(unset)

    def dump(self, filename: Path, partial=False):
        """Dump the H5Group object tree into a file.

        Args:
            filename: Path to dump the HDF5Group object tree to.
            partial: If False, will raise an error if any H5Dataset is not written to.

        Returns: None
        """
        with h5py.File(filename, "w") as h5file:
            self._dump(h5file, PurePosixPath("/"))

        if not partial:
            self._check_all_modified()

    @contextmanager
    def dumper(self, filename: Path, partial=False):
        """Context manager to dump the H5Group object tree into a file.

        Inside the context manager, Datasets can be assigned to, which will write
        that data to the file.

        At the cleanup stage, if partial is False, this context manager will ensure all Datasets have been written to.

        Args:
            filename: Path to dump the HDF5Group object tree to.
            partial: If False, will raise an error if any H5Dataset is not written to.

        Returns: None
        """
        with h5py.File(filename, "w") as h5file:
            self._h5file = h5file
            self._dump(h5file, PurePosixPath("/"))

            yield self

            self.close()

        if not partial:
            self._check_all_modified()
