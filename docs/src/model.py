from h5pydantic import H5Dataset, H5Group


class Baseline(H5Group):
    temperature: float
    humidity: float


class Metadata(H5Group):
    start: Baseline
    end: Baseline


class Acquisition(H5Dataset):
    _shape = (1024, 1024)
    _dtype = "int32"
    beamstop: int


class Experiment(H5Group):
    metadata: Metadata
    data: list[Acquisition]
