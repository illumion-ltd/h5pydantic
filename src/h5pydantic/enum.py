from pathlib import PurePosixPath

import h5py
import h5py.h5t

import pydantic.fields


def _h5enum_dump(h5file: h5py.File, container, key: str, value: int, fieldtype: pydantic.fields.ModelField):
    # FIXME look for previous type? maybe cache it in the class?
    h5type = h5py.h5t.enum_create(fieldtype.type_._member_type_.h5pyid)
    for (member_name, member_value) in fieldtype.type_.__members__.items():
        h5type.enum_insert(member_name.encode("ascii"), member_value)

        container.attrs.create(key, dtype=h5type.dtype, data=value)


def _h5enum_load(h5file: h5py.File, prefix: PurePosixPath, key: str, field: pydantic.fields.ModelField):
    return field.type_(h5file[str(prefix)].attrs[key])
