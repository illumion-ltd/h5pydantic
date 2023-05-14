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

