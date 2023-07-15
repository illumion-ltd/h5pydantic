from h5pydantic import H5Group

import pytest

@pytest.fixture(scope="session")
def hdf_path(tmp_path_factory):
    return tmp_path_factory.mktemp("data") / "test.hdf"

def test_invalid_container_classes():
    with pytest.raises(ValueError, match="only handles list containers"):
        class DictContainer(H5Group):
            container: dict[str, str] = {}


def test_invalid_value_produces_useful_exception(hdf_path):
    class Experiment(H5Group):
        number: int = None

    exp = Experiment()

    with pytest.raises(ValueError, match="While attempting to save attribute ``number`` = ``None``") as exc_info:
        exp.dump(hdf_path)

    cause = exc_info.value.__cause__
    assert str(cause) == "Object dtype dtype('O') has no native HDF5 equivalent"

# FIXME test an extra argument is not allowed
# FIXME test assignment is validated
# FIXME test that list append is validated
# FIXME there should be a root validator making sure all types are hdf5 friendly
