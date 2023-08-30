from importlib import metadata

__version__ = metadata.version(__package__)

from .enum import H5IntEnum
from .model import H5Dataset, H5DatasetConfig, H5Group
from .types import H5Int32, H5Int64
