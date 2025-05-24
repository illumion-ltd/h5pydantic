from h5pydantic import H5Group, H5Dataset, H5Int32

class Position(H5Group):
    x: H5Int32
    y: H5Int32

class CalibImage(H5Dataset, dtype=H5Int32, shape=(3,2)):
    pass

class Calibration(H5Group):
  no_beam: CalibImage = CalibImage()
  position: Position

class Experiment(H5Group):
    calibration: Calibration
