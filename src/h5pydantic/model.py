import h5py
from pydantic import BaseModel, PrivateAttr, StrictInt, StrictStr

import numpy

from abc import abstractmethod
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from enum import Enum
import types

from typing import get_origin, get_args
from typing import Any, Optional, Union
from typing_extensions import Self, Type

from .enum import _h5enum_dump, _h5enum_load
from .exceptions import H5PartialDump
from .types import H5Type, _pytype_to_h5type

_H5Container = Union[h5py.Group, h5py.Dataset]

import logging

logger = logging.getLogger('h5pydantic_logger')

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
            # logger.info(f"ALIAS: {field.alias}, TYPE: {field.type_}, required: {field.required}, outer type: {field.outer_type_}, origin: {get_origin(field.outer_type_)}")

            # Allow h5py to work with unions - only currently checks against data shape
            if get_origin(field.outer_type_) == Union:
                # If the field is optional and not found in HDF5 then set to any model so 
                # the dictionary item can be set to None later on
                if field.required is False and str(prefix / field.alias) not in h5file:
                    field.type_ = get_args(field.outer_type_)[0]
                else:
                    np_dataset = h5file[str(prefix / field.alias)][()]
                    
                    # if data dimensions match check if shape matches any datamodel in the union
                    model_match: bool = True
                    for data_model in get_args(field.outer_type_):
                        model_match = True
                        if len(data_model._h5config.shape) == len(np_dataset.shape):
                            for idx, data_dim in enumerate(data_model._h5config.shape):
                                if data_dim != -1 and data_dim != np_dataset.shape[idx]:
                                    model_match = False
                        else:
                            model_match = False

                        if model_match:
                            logger.info(f"UNION FOUND: {field.alias}, data model {data_model} shape match")
                            field.type_ = data_model
                            break
                    
                    if not model_match:
                        raise(TypeError(f"Could not find suitable data model in Union to match data shape: {np_dataset.shape}"))
                    
            if get_origin(field.outer_type_) == list:    # isinstance(field.outer_type_, types.GenericAlias):
                if field.required is False and (str(prefix / field.alias) not in h5file or field.alias not in h5file[str(prefix)].attrs.keys()):
                    d[field.alias] = None
                    logger.info(f"Optional field {key} not present in this file")
                else:
                    if field.alias in h5file[str(prefix)].attrs.keys():
                        # TODO add types that aren't ints
                        d[field.alias] = [int(i) for i in h5file[str(prefix)].attrs[field.alias]]
                    else:
                        d[field.alias] = []
                        indexes = [int(i) for i in h5file[str(prefix / field.alias)].keys()]
                        indexes.sort()
                        for i in indexes:
                            # FIXME This doesn't check a lot of cases.
                            d[field.alias].insert(i, field.type_._load(h5file, prefix / field.alias / str(i)))

            elif issubclass(field.type_, _H5Base):
                if field.required is False and str(prefix / field.alias) not in h5file:
                    d[field.alias] = None
                    logger.info(f"Optional field {key} not present in this file")
                else:
                    d[field.alias] = field.type_._load(h5file, prefix / field.alias)

            elif issubclass(field.type_, Enum):
                d[field.alias] = _h5enum_load(h5file, prefix, field.alias, field)

            else:
                if field.required is False and field.alias not in h5file[str(prefix)].attrs:
                    d[field.alias] = None
                    logger.info(f"Optional attribute {key} from path {prefix} not present in this file")
                else:
                    d[field.alias] = h5file[str(prefix)].attrs[field.alias]

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

        data_type = str(dset.dtype)
        
        #TODO do we need these cheks now 'require_dataset' is being used?
        # Check Dimensions: 
        if len(cls._h5config.shape) != len(dset.shape):
            raise ValueError(f"{prefix}: Dimensions of model ({len(cls._h5config.shape)}) dont match dimensions of H5 data: {len(dset.shape)}")
        
        # Check Shape: 
        for idx, data_dim in enumerate(cls._h5config.shape):
            if data_dim != -1 and data_dim != dset.shape[idx]:
                raise ValueError(f"{prefix}: Model Shape {cls._h5config.shape} does not match H5 data shape {dset.shape}")

        # Check Data Type:
        if str(data_type) == 'object' and  (cls._h5config.dtype.numpy != numpy.bytes_):
            # string type imports from h5 as 'object'
            raise ValueError(f"{prefix}: Model data type {cls._h5config.dtype.numpy} (string) does not match H5 data type {data_type}")
        elif isinstance(dset.dtype, numpy.dtypes.VoidDType) and  (cls._h5config.dtype.numpy != numpy.bytes_):
            # Compoud data type imports from h5 as VoidDType
            raise ValueError(f"Compound types do not match in model and data")
        elif data_type != 'object' and not isinstance(dset.dtype, numpy.dtypes.VoidDType) and dset.dtype != cls._h5config.dtype.numpy:
            raise ValueError(f"{prefix}:Model data type {cls._h5config.dtype.numpy} does not match H5 data type {dset.dtype}")
            
        # Allows model to deal with compound data types
        if isinstance(dset.dtype, numpy.dtypes.VoidDType):
            data_type = str(dset.dtype.__class__.__name__)

        logger.info(f"VALIDATED {cls.__name__}: Data shape [{cls._h5config.shape}={dset.shape}] and data type {cls._h5config.dtype.numpy} match")
        
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
