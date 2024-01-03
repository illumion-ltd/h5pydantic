from model import Experiment, Acquisition, Baseline, Metadata

import numpy as np
from pathlib import Path

experiment = Experiment(data=[Acquisition(beamstop=11), Acquisition(beamstop=12)],
                        metadata=Metadata(start=Baseline(temperature=25.0, humidity=0.4),
                                          end=Baseline(temperature=26.0, humidity=0.4)))

with experiment.dumper(Path("experiment.hdf")):
    experiment.data[0][()] = np.random.randint(255, size=(3, 5))
    experiment.data[1][()] = np.random.randint(255, size=(3, 5))
