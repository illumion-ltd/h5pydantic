from model import Experiment
from pathlib import Path

with Experiment.load(Path("experiment.hdf")) as experiment:
    print(experiment.data[1].data_[:])
    print(experiment.metadata.start.temperature)
