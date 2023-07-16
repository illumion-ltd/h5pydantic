from hypothesis import given, strategies as st
from pydantic import create_model

from h5pydantic import H5Group, H5Dataset
from h5pydantic import H5Integer32, H5Integer64

import numpy

import string
import io


def classname_st():
    """A strategy that produces a valid python class name."""
    head_alphabet = string.ascii_uppercase
    tail_alphabet = head_alphabet + string.digits + "_"

    return st.builds(
        lambda a, b: a + b,
        st.text(head_alphabet, min_size=1, max_size=1),
        st.text(tail_alphabet))


def varname_st():
    """A strategy that produces a valid python variable name"""

    head_alphabet = string.ascii_letters
    tail_alphabet = head_alphabet + string.digits + "_"

    return st.builds(
        lambda a, b: a + b,
        st.text(head_alphabet, min_size=1, max_size=1),
        st.text(tail_alphabet))

# TODO add datasets to values
# TODO add lists
# TODO add enum
# TODO handle NaN values, maybe get rid of == and have a _data_equality
@st.composite
def type_and_value_st(draw):
    """A strategy that produces a valid type and associated value."""
    # FIXME generate these on the fly
    class DummyDataSet(H5Dataset, shape=(2,3), dtype=H5Integer32):
        pass

    dtype = draw(st.sampled_from([H5Integer32, H5Integer64, 
                                  float, str,
                                  H5Group,
                                  #H5Dataset,
                                  ]))
    
    if dtype is H5Integer32:
        strat = st.integers(min_value=H5Integer32.ge, max_value=H5Integer32.le)
    elif dtype is H5Integer64:
        strat = st.integers(min_value=H5Integer64.ge, max_value=H5Integer64.le)
    elif dtype is float:
        strat = st.floats(allow_nan=False)
    elif dtype is str:
        strat = st.text(string.printable)
    elif dtype is H5Dataset:
        # FIXME mix it up a bit
        dtype = DummyDataSet
        strat = st.just(DummyDataSet())
    elif dtype is H5Group:
        group = draw(st.deferred(lambda: group_st()))
        return (group, group())

    return (dtype, draw(strat))


def populate_datasets(group: H5Group):
    for name, field in group.__fields__.items():
        if issubclass(field.type_, H5Dataset):
            value = getattr(group, name)
            value.data(numpy.random(value._h5config.shape, 10))


@st.composite
def group_st(draw):
    classname = draw(classname_st())

    d = draw(st.dictionaries(min_size=1,
                             keys=varname_st(),
                             values=type_and_value_st()))

    return create_model(classname, __base__=H5Group, **d)


@given(group=group_st())
def test_roundtrip(group, hdf_path):
    model = group()
    populate_datasets(group)

    model.dump(hdf_path)

    with group.load(hdf_path) as loaded:
        assert model == loaded
