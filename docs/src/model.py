from h5pydantic import H5Dataset, H5Group, H5Int64


class Baseline(H5Group):
    temperature: float
    humidity: float


class Metadata(H5Group):
    start: Baseline
    end: Baseline


class Acquisition(H5Dataset, shape=(3,5), dtype=H5Int64):
    beamstop: H5Int64


class Experiment(H5Group):
    metadata: Metadata
    data: list[Acquisition] = []
