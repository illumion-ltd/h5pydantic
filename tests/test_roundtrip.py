from hypothesis import given, strategies as st
from pydantic import create_model

from h5pydantic import H5Group, H5Integer32, H5Integer64

import pytest

import string
import io

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
    dtype, strat = draw(st.sampled_from([(H5Integer32, st.integers(min_value=H5Integer32.ge, max_value=H5Integer32.le)),
                                         (H5Integer64, st.integers(min_value=H5Integer64.ge, max_value=H5Integer64.le)),
                                         (float, st.floats(allow_nan=False)),
                                         (str, st.text(string.printable)),
                                         ]))

    return (dtype, draw(strat))


@given(d=st.dictionaries(min_size=1,
                         keys=varname(),
                         values=type_value_tup()))
def test_roundtrip(d):
    d["__base__"] = H5Group

    dynamic_model = create_model("dynamic_model", **d)

    output = dynamic_model()

    bio = io.BytesIO()
    output.dump(bio)

    with dynamic_model.load(bio) as loaded:
        assert output == loaded

