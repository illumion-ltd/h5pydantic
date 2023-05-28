from hypothesis import given, strategies as st
from hypothesis.strategies import composite
from pydantic import create_model

from h5pydantic import H5Group

import pytest

import string


def varname():
    """A strategy that produces a valid python variable name"""

    head_alphabet = string.ascii_letters
    tail_alphabet = head_alphabet + string.digits + "_"

    return st.builds(
        lambda a, b: a + b,
        st.text(head_alphabet, min_size=1, max_size=1),
        st.text(tail_alphabet))

# TODO add datasets to values, make it recursive.
# TODO handle NaN values
# TODO calculcate the integers min/max properly
@composite
def value(draw, types=st.one_of(st.integers(min_value=-2**63, max_value=2**63), st.floats(allow_nan=False))):
    """A strategy that produced a valid HD5Group dictionary definition."""
    val = draw(types)
    return (type(val), val)



@pytest.fixture(scope="session")
def hdf_path(tmp_path_factory):
    return tmp_path_factory.mktemp("data") / "roundtrip.hdf"

@given(d=st.dictionaries(min_size=1,
                         keys=varname(),
                         values=value()))
def test_roundtrip(d, hdf_path):
    d["__base__"] = H5Group

    dynamic_model = create_model("dynamic_model", **d)

    output = dynamic_model()

    output.dump(hdf_path)

    with dynamic_model.load(hdf_path) as input:
        assert output == input
