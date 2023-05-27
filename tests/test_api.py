from h5pydantic import H5Group

import pytest


def test_invalid_container_classes():
    class DictContainer(H5Group):
        container: dict[str, str] = {}

    with pytest.raises(ValueError, match="only handles list containers"):
        c = DictContainer()

# FIXME test an extra argument is not allowed
# FIXME test assignment is validated
# FIXME test that list append is validated
