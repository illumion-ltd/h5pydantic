from pydantic import BaseModel

from pathlib import Path

import h5py


class H5Group(BaseModel):
    """Maps from a HDF5 file to a set of Python classes."""

    @classmethod
    def _load(cls: BaseModel, h5file: h5py.File, prefix: Path):
        d = {}
        for key, field in cls.__fields__.items():
            if issubclass(field.type_, H5Group):
                d[key] = field.type_._load(h5file, prefix / key)
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
        for key in self.__fields__:
            value = getattr(self, key)
            if isinstance(value, H5Group):
                value._dump(h5file, prefix / key)
            else:
                group.attrs[key] = getattr(self, key)

    def dump(self, filename: Path):
        """Dump the H5Group object tree into a file."""
        with h5py.File(filename, "w") as h5file:
            self._dump(h5file, Path("/"))
