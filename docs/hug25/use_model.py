from model import Experiment

exp = Experiment(calibration={"position": {"x": 247, "y": 253}})
exp.calibration.no_beam.data([[0, 0, 1], [0, 0, 0]])
exp.dump("experiment.hdf5")
