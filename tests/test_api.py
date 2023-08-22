from h5pydantic import H5Group

import pytest

def test_invalid_container_classes():
    with pytest.raises(ValueError, match="only handles list containers"):
        class DictContainer(H5Group):
            container: dict[str, str] = {}


# FIXME test an extra argument is not allowed
# FIXME test assignment is validated
# FIXME test that list append is validated
# FIXME there should be a root validator making sure all types are hdf5 friendly
