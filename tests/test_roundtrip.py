from hypothesis import given, strategies as st
from pydantic import create_model

from h5pydantic import H5Group, H5Dataset
from h5pydantic import H5Integer32, H5Integer64

import numpy

import pytest

import string
import io
import types

def varname():
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
# TODO make it recursive.
# TODO handle NaN values, maybe get rid of == and have a _data_equality
@st.composite
def type_value_tup(draw):
    # FIXME generate these on the fly
    class DummyDataSet(H5Dataset, shape=(2,3), dtype=H5Integer32):
        pass

    dtype = draw(st.sampled_from([H5Integer32, H5Integer64, 
                                  float, str,
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

    return (dtype, draw(strat))


def populate_datasets(group: H5Group):
    for name, field in group.__fields__.items():
        if issubclass(field.type_, H5Dataset):

            # FIXME randomise the fill value)
            value = getattr(group, name)
            value.data(numpy.full(value._h5config.shape, 10))


@given(d=st.dictionaries(min_size=1,
                         keys=varname(),
                         values=type_value_tup()))
def test_roundtrip(d):
    d["__base__"] = H5Group

    dynamic_model = create_model("dynamic_model", **d)

    output = dynamic_model()

    populate_datasets(output)

    bio = io.BytesIO()
    output.dump(bio)

    with dynamic_model.load(bio) as loaded:
        for key, field in loaded.__fields__.items():
            if issubclass(field.type_, H5Dataset):
                val = getattr(loaded, key)
                print("loaded", val._data)
            

        assert output == loaded

