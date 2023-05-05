from pathlib import Path

class HDF5:
    """Maps from a HDF5 file to a set of Python classes."""

    def __init__(self):
        pass

    @classmethod
    def load(filename: Path) -> tuple["HDF5", list[str]]:
        """Load a file into a HDF5 set of objects.

        Returns the object, plus a list of any unmapped keys.
        """
        pass

    def dump(self, filename: Path):
        """Dumps the HDF5 object set into a file."""
        pass
