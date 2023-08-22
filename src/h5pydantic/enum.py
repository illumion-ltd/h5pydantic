from pathlib import PurePosixPath

import h5py
import h5py.h5t

import pydantic.fields

from enum import Enum, IntEnum

class H5Enum(int, Enum):
    @classmethod
    def _dump(cls, h5file: h5py.File, container, key: str, value: int, fieldtype: pydantic.fields.ModelField):
        # FIXME look for previous type? maybe cache it in the class?
        h5type = h5py.h5t.enum_create(fieldtype.type_.dtype().h5pyid)
        for (member_name, member_value) in fieldtype.type_.__members__.items():
            h5type.enum_insert(member_name.encode("ascii"), member_value)

        container.attrs.create(key, dtype=h5type.dtype, data=value)

    @classmethod
    def _load(cls, h5file: h5py.File, prefix: PurePosixPath, key: str, field: pydantic.fields.ModelField):
        return field.type_(h5file[str(prefix)].attrs[key])


class H5IntEnum(IntEnum):
    """Wraps the HDF5 Integer Enum Type.

    The dtype class keywoard argument is mandatory.
    """
    def __init_subclass__(self, **kwds):
        # FIXME raise a nice alert if dtype kwarg is missing.
        self.__class__.dtype = lambda x: kwds["dtype"]
