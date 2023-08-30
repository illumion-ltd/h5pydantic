from h5pydantic import H5Dataset, H5Int64

import pytest


def test_shape_ints_are_strictly_ints():
    with pytest.raises(ValueError, match="value is not a valid integer"):
        class FloatShape(H5Dataset, shape=(1.0, 2.0), dtype=H5Int64):
            pass

# FIXME check for strict ints in dataset shape tuples, don't accept floats
