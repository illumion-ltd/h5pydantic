from h5pydantic import H5Group, H5Dataset, H5Int32

class Position(H5Group):
    x: H5Int32
    y: H5Int32

class CalibPicture(H5Dataset, dtype=H5Int32, shape=(3,2)):
    pass

class Calibration(H5Group):
  no_beam: CalibPicture
  position: Position
