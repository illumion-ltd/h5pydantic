from hypothesis import given, strategies as st
from pydantic import create_model
from h5pydantic import H5Group, H5Dataset, H5Integer32, H5Integer64
import numpy
import string

def name_str(head_alphabet):
    tail_alphabet = head_alphabet + string.digits + "_"
    return st.builds(str.__add__, st.sampled_from(head_alphabet), st.text(tail_alphabet))

def classname_st(): return name_str(string.ascii_uppercase)
def varname_st(): return name_str(string.ascii_letters)

@st.composite
def type_and_value_st(draw):
    class DummyDataSet(H5Dataset, shape=(2,3), dtype=H5Integer32): pass
    dtype = draw(st.sampled_from([H5Integer32, H5Integer64, float, str, H5Dataset, H5Group]))
    if dtype is H5Integer32:
        strat = st.integers(min_value=H5Integer32.ge, max_value=H5Integer32.le)
    elif dtype is H5Integer64:
        strat = st.integers(min_value=H5Integer64.ge, max_value=H5Integer64.le)
    elif dtype is float:
        strat = st.floats(allow_nan=False)
    elif dtype is str:
        strat = st.text(string.printable)
    elif dtype is H5Dataset:
        dataset = DummyDataSet()
        dataset.data(numpy.random.randint(-100, 100, size=dataset._h5config.shape))
        return (DummyDataSet, dataset)
    elif dtype is H5Group:
        group = draw(st.deferred(lambda: group_st()))
        return (group, group())
    return (dtype, draw(strat))

@st.composite
def group_st(draw):
    classname = draw(classname_st())
    d = draw(st.dictionaries(min_size=1, keys=varname_st(), values=type_and_value_st()))
    return create_model(classname, __base__=H5Group, **d)

@given(group=group_st())
def test_roundtrip(group, hdf_path):
    model = group()
    model.dump(hdf_path)
    with group.load(hdf_path) as loaded:
        assert model == loaded
