import h5py

h5file = h5py.File("experiment.hdf5", "w")

calibration_group = h5file.create_group("calibration")

dataset = calibration_group.create_dataset("no_beam", 
                                           [0, 0, 0, 1, 0, 0])

position = calibration_group.create_group("position")
position.attrs["x"] = 247
position.attrs["y"] = 253
