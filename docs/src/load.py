from model import Experiment
from pathlib import Path

experiment, unparsed = Experiment.load(Path("experiment.hdf"))

print(experiment.data[1].data_)
print(experiment.metadata.start.temperature)
