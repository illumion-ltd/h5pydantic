from h5pydantic import H5Group, H5Int64
from typing import Optional


class Inner(H5Group):
    once: str


class Group(H5Group):
    optional_magic: Optional[H5Int64] = None
    optional_group: Optional[Inner] = None


def test_optional_field_saved(hdf_path):
    group = Group(optional_magic=3)

    group.dump(hdf_path)

    loaded = Group.load(hdf_path)

    assert loaded.optional_magic == 3


def test_optional_field_not_saved(hdf_path):
    group = Group()

    group.dump(hdf_path)

    loaded = Group.load(hdf_path)

    assert loaded.optional_magic is None


def test_optional_group_saved(hdf_path):
    print(hdf_path)

    group = Group(optional_group=Inner(once="yup"))

    group.dump(hdf_path)

    print("dumped", group)

    loaded = Group.load(hdf_path)

    print("loaded", loaded)
    assert loaded.optional_group.once == "yup"


def test_optional_group_not_saved():
    pass


def test_optional_dataset_not_saved():
    pass


def test_optional_dataset_saved():
    pass


def test_optional_enum_not_saved():
    pass


def test_optional_enum_saved():
    pass


def test_optional_list_container_not_saved():
    pass


def test_optional_list_container_saved():
    pass
