from hypothesis import given, strategies as st
from h5pydantic import H5Group, H5Dataset, H5DatasetConfig, H5Integer32, H5Integer64
import numpy, string, types

def name_str(head_alphabet):
    return st.builds(str.__add__, st.sampled_from(head_alphabet), st.text(head_alphabet + string.digits + "_"))

def classname_st():
    return name_str(string.ascii_uppercase)

def varname_st():
    return name_str(string.ascii_letters)

@st.composite
def type_and_value_st(draw, dataset: bool = True):
    dtype = draw(st.sampled_from([H5Integer32, H5Integer64, float, str] + [H5Dataset, H5Group] * dataset))
    return {H5Integer32: (lambda: (dtype, draw(st.integers(min_value=H5Integer32.ge, max_value=H5Integer32.le)))),
            H5Integer64: (lambda: (dtype, draw(st.integers(min_value=H5Integer64.ge, max_value=H5Integer64.le)))),
            float:       (lambda: (dtype, draw(st.floats(allow_nan=False)))),
            str:         (lambda: (dtype, draw(st.text(string.printable)))),
            H5Dataset:   (lambda: (draw(st.deferred(lambda: dataset_st())))),
            H5Group:     (lambda: (draw(st.deferred(lambda: group_st())))),
            }[dtype]()

@st.composite
def dataset_st(draw):
    classname = draw(classname_st())
    ndims = draw(st.integers(min_value=1, max_value=3))
    shape = tuple(draw(st.integers(min_value=2, max_value=5)) for dim in range(ndims))
    d = draw(st.dictionaries(min_size=1, keys=varname_st(), values=type_and_value_st(False)))
    dtype = types.new_class(classname, (H5Dataset,), kwds={"shape": shape, "dtype": H5Integer32})
    value = dtype()
    value.data(numpy.random.randint(-100, 100, size=shape))
    return (dtype, value)

@st.composite
def group_st(draw):
    classname = draw(classname_st())
    d = draw(st.dictionaries(min_size=1, keys=varname_st(), values=type_and_value_st()))
    dtype = types.new_class(classname, (H5Group,), d)
    value = dtype()
    return (dtype, value)

@given(group=group_st())
def test_roundtrip(group, hdf_path):
    klass, model = group
    model.dump(hdf_path)
    with klass.load(hdf_path) as loaded:
        assert model == loaded
