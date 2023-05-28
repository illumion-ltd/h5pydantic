from importlib import metadata

__version__ = metadata.version(__package__)

from .model import H5Dataset, H5Group
from .types import H5Integer64
