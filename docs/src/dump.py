from model import Experiment, Acquisition, Baseline, Metadata

import numpy
from pathlib import Path

experiment = Experiment(metadata=Metadata(start=Baseline(temperature=25.0, humidity=0.4),
                                          end=Baseline(temperature=26.0, humidity=0.4)))

acq = Acquisition(beamstop=11)
acq.data(numpy.random.randint(255, size=Acquisition._h5config.shape))
experiment.data.append(acq)

acq = Acquisition(beamstop=12)
acq.data(numpy.random.randint(255, size=Acquisition._h5config.shape))
experiment.data.append(acq)

experiment.dump(Path("experiment.hdf"))
