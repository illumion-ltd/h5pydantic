from h5pydantic import H5Dataset, H5Group, H5Integer64


class Baseline(H5Group):
    temperature: float
    humidity: float


class Metadata(H5Group):
    start: Baseline
    end: Baseline


class Acquisition(H5Dataset, shape=(3,5), dtype=H5Integer64):
    beamstop: int


class Experiment(H5Group):
    metadata: Metadata
    data: list[Acquisition] = []
