from model import Experiment

exp = Experiment.load("experiment.hdf5")
(x, y) = exp.calibration.position.x, exp.calibration.position.y
