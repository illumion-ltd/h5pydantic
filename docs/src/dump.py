from model import Experiment

import numpy
from pathlib import Path

shape = (1024, 1024)

experiment = Experiment(metadata={"start": {"temperature": 25.0, "humidity": 0.4},
                                  "end": {"temperature": 26.0, "humidity": 0.4}},
                        data=[{"_data": numpy.random.randint(255, size=shape), "beamstop": 10},
                              {"_data": numpy.random.randint(255, size=shape), "beamstop": 11},
                              {"_data": numpy.random.randint(255, size=shape), "beamstop": 12}])

experiment.dump(Path("experiment.hdf"))
