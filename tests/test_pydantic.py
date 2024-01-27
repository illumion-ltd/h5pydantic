# Tests for hacky pydantic things we're doing.

from h5pydantic import H5Group, H5Dataset

from pydantic import StrictStr

class Experiment(H5Group):
    name: str


class Foo(H5Group):
    name: StrictStr

def test_coerce_str_to_strictstr():
    exp = Experiment(name="foo")

    field = exp.__fields__["name"]

    assert field.type_ is StrictStr

# FIXME test other string types, like maxlen=10, annotated(SnakeCase) etc. are coerced.
# FIXME test all this in a dataset fields, as well as a group

