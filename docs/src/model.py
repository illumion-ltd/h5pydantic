from h5pydantic import H5Dataset, H5Group


class Baseline(H5Group):
    temperature: float
    humidity: float


class Metadata(H5Group):
    start: Baseline
    end: Baseline


class Acquisition(H5Dataset):
    shape_: tuple[int, ...] = (3, 5)
    dtype_: str = "int32"
    beamstop: int = None


class Experiment(H5Group):
    metadata: Metadata
    data: list[Acquisition]
