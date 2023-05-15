from hypothesis import given, strategies as st
import string


def varname():
    """A strategy that produces a valid python variable name"""

    head_alphabet = string.ascii_letters + "_"
    tail_alphabet = head_alphabet + string.digits

    return st.builds(
        lambda a, b: a + b,
        st.text(head_alphabet, min_size=1, max_size=1),
        st.text(tail_alphabet))

rectangle_lists = st.integers(min_value=0, max_value=10).flatmap(

    lambda n: lists(lists(integers(), min_size=n, max_size=n))

)

# TODO add datasets to values, make it recursive.
def values():
    """A strategy that produced a valid HD5Group dictionary definition."""

    def st_value(t):
        

    return st.one_of(st.integers(), st.floats()).flatmap(st_value)


@given(st.dictionaries(min_size=1,
                       keys=varname(),
                       values=st.one_of(st.integers(), st.floats())))
def test_roundtrip(d):
    print(d)
    assert False
