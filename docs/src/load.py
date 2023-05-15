from model import Experiment
from pathlib import Path

experiment = Experiment.load(Path("experiment.hdf"))

data1 = experiment.data[1]._data
starting_temp = experiment.metadata.start.temperature
