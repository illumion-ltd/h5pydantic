from h5pydantic import H5Group, H5Dataset, H5Int64

import pytest


class Data(H5Dataset, shape=(2,2), dtype=H5Int64):
    intmeta: int


class Experiment(H5Group):
    aint: H5Int64
    afloat: float
    astr: str
    ilist: list[int]
    data: Data


def test_assignment_validation():
    exp = Experiment(aint=10, afloat=3.14, astr="foobar", ilist=[1, 2, 3],
                     data=Data(intmeta=10))

    exp.aint = 11
    exp.afloat = 10.99
    exp.astr = "barry sally"
    exp.ilist = [10, 11, 12]
    exp.data.intmeta = 22

    with pytest.raises(ValueError):
        exp.aint = "definitely not an int"

    with pytest.raises(ValueError):
        exp.afloat = "definitely not a float"

    with pytest.raises(ValueError):
        exp.astr = 3

    with pytest.raises(ValueError):
        exp.alist = "not a list"

# FIXME check dataset, check shape and dtype and other fields can't be modified
# FIXME list of groups, list of datasets?
# FIXME test validation of default values
# FIXME test that None is ok for optional assignment
