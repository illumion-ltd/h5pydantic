import pytest

@pytest.fixture(scope="session")
def hdf_path(tmp_path_factory):
    return tmp_path_factory.mktemp("data") / "test.hdf"
