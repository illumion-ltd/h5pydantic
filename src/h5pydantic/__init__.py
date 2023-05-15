import h5py
from pydantic import BaseModel
import numpy


from pathlib import Path, PurePosixPath
import types

from typing import Union


class _AbstractH5Base:
    """An implementation detail, to share the _load and _dump API."""

    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> Union[h5py.Group, h5py.Dataset]:
        pass

    def _dump_children(self, container, h5file: h5py.File, prefix: PurePosixPath):
        for key, field in self.__fields__.items():
            # FIXME I think I should be explicitly testing these keys against a known list, at init time though.
            if key.endswith("_"):
                continue
            value = getattr(self, key)
            if isinstance(value, _AbstractH5Base):
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
    def _load(cls: BaseModel, h5file: h5py.File, prefix: PurePosixPath) -> tuple["H5Group", list[str]]:
        pass


class H5Dataset(_AbstractH5Base, BaseModel):
    """A pydantic Basemodel specifying a HDF5 Dataset."""

    class Config:
        # Allows numpy.ndarray (which doesn't have a validator).
        arbitrary_types_allowed = True

        # Allows us to use field names starting with underscore
        underscore_attrs_are_private = True
    # FIXME check that all underscore attributes are special attributes

    # FIXME refactor _load/_dump apis
    # There are a *lot* of dataset features to be supported as optional flags, compression, chunking etc.
    # FIXME test for attributes on datasets
    # FIXME I'm not comfortable with shadowing these fields like this,
    # but it's nice to have some ns to put config variables in.
    shape_: tuple[int]
    dtype_: str = "f"

    # FIXME is it possible to initialise this after we've got shape_ and dtype_ in the instance?
    data_: numpy.ndarray = None

    def _dump_container(self, h5file: h5py.File, prefix: PurePosixPath) -> h5py.Dataset:
        # FIXME check that the shape of data matches
        # FIXME add in all the other flags
        dataset = h5file.require_dataset(str(prefix), shape=self.shape_, dtype=self.dtype_)
        dataset[:] = self.data_
        return dataset

    @classmethod
    def _load(cls: BaseModel, h5file: h5py.File, prefix: PurePosixPath) -> tuple["H5Group", list[str]]:
        # Really should be verifying all of the details match the class.
        data = h5file[str(prefix)]
        d = {"shape": data.shape, "dtype": data.dtype, "data": data}
        return cls.parse_obj(d)


class H5Group(_AbstractH5Base, BaseModel):
    """A pydantic BaseModel specifying a HDF5 Group."""

    # Check for attributes that start with underscore

    @classmethod
    def _load(cls: BaseModel, h5file: h5py.File, prefix: PurePosixPath):
        d = {}
        for key, field in cls.__fields__.items():
            if isinstance(field.outer_type_, types.GenericAlias):
                # FIXME clearly I should not be looking at these attributes.
                if not issubclass(field.outer_type_.__origin__, list):
                    raise ValueError("h5pydantic only handles list containers")

                if not issubclass(field.type_, H5Group):
                    # FIXME should definitely handle other things.
                    raise ValueError("h5pydantic only handles H5Groups as a container element")

                d[key] = []
                indexes = [int(i) for i in h5file[str(prefix / key)].keys()]
                indexes.sort()
                for i in indexes:
                    # FIXME This doesn't check a lot of cases.
                    d[key].insert(i, field.type_._load(h5file, prefix / key / str(i)))
            elif issubclass(field.type_, _AbstractH5Base):
                d[key] = field.type_._load(h5file, prefix / key)
            elif issubclass(field.type_, list):
                pass
            else:
                d[key] = h5file[str(prefix)].attrs[key]

        return cls.parse_obj(d)

    @classmethod
    def load(cls: BaseModel, filename: Path) -> tuple["H5Group", list[str]]:
        """Load a file into a tree of H5Group models.

        Args:
            filename: Path of HDF5 to load.

        Returns:
            A tuple, the first object being the parsed H5Group model, the second being a list of unparsed keys.
        """
        with h5py.File(filename, "r") as h5file:
            # TODO actually build up the list of unparsed keys
            return cls._load(h5file, PurePosixPath("/")), []

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

