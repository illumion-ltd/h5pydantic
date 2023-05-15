from model import Experiment, Acquisition

import numpy
from pathlib import Path

shape = (3, 5)

experiment = Experiment(metadata={"start": {"temperature": 25.0, "humidity": 0.4},
                                  "end": {"temperature": 26.0, "humidity": 0.4}},
                        data=[])

experiment.data.append(Acquisition(data_=numpy.random.randint(255, size=shape), beamstop=10))
experiment.data.append(Acquisition(data_=numpy.random.randint(255, size=shape), beamstop=11))
experiment.data.append(Acquisition(data_=numpy.random.randint(255, size=shape), beamstop=12))

experiment.dump(Path("experiment.hdf"))
