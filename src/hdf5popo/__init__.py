from pydantic import BaseModel

from pathlib import Path

import h5py


class HDF5DataProduct(BaseModel):
    """Maps from a HDF5 file to a set of Python classes."""
    __group__ = "/"


    @classmethod
    def load(filename: Path) -> tuple["HDF5", list[str]]:
        """Load a file into a HDF5 set of objects.

        Returns the object, plus a list of any unmapped keys.
        """
        pass

    def dump(self, filename: Path):
        """Dumps the HDF5 object set into a file."""
        with h5py.File(filename, "w") as f:

            group = f[self.__group__]
            for key in self.__fields__:
                group.attrs[key] = getattr(self, key)

    def __setattr__(self, name, value):
        if name not in self.__dict__:
            raise NameError(f"HDF5 attribute '{name}' not defined for '{self.__class__}'")

        # TODO check the type

        self.name = value
