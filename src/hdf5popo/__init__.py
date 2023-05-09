from pydantic import BaseModel

from pathlib import Path

import h5py

import types


class H5Group(BaseModel):
    """A pydantic BaseModel describing a HDF5 Group."""

    @classmethod
    def _load(cls: BaseModel, h5file: h5py.File, prefix: Path):
        d = {}
        for key, field in cls.__fields__.items():
            if isinstance(field.outer_type_, types.GenericAlias):
                # FIXME clearly I should not be looking at these attributes.
                if not issubclass(field.outer_type_.__origin__, list):
                    raise ValueError("H5Popo only handles list containers")

                if not issubclass(field.type_, H5Group):
                    raise ValueError("H5Popo only handles H5Groups as a container element")

                d[key] = []
                indexes = [int(i) for i in h5file[str(prefix / key)].keys()]
                indexes.sort()
                for i in indexes:
                    # FIXME This doesn't check a lot of cases.
                    d[key].insert(i, field.type_._load(h5file, prefix / key / str(i)))
            elif issubclass(field.type_, H5Group):
                d[key] = field.type_._load(h5file, prefix / key)
            elif issubclass(field.type_, list):
                pass
            else:
                d[key] = h5file[str(prefix)].attrs[key]

        return cls.parse_obj(d)

    @classmethod
    def load(cls: BaseModel, filename: Path) -> tuple["H5Group", list[str]]:
        """Load a file into a tree of H5Group models.

        Returns the object, plus a list of any unmapped keys.
        """
        with h5py.File(filename, "r") as h5file:
            # TODO actually build up the list of unparsed keys
            return cls._load(h5file, Path("/")), []

    def _dump(self, h5file: h5py.File, prefix: Path):
        group = h5file.require_group(str(prefix))
        for key, field in self.__fields__.items():
            value = getattr(self, key)
            if isinstance(value, H5Group):
                value._dump(h5file, prefix / key)
            elif isinstance(value, list):
                for i, elem in enumerate(value):
                    elem._dump(h5file, prefix / key / str(i))
            else:
                group.attrs[key] = getattr(self, key)

    def dump(self, filename: Path):
        """Dump the H5Group object tree into a file."""
        with h5py.File(filename, "w") as h5file:
            self._dump(h5file, Path("/"))
