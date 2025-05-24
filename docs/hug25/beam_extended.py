from h5pydantic import H5Group, H5Int32
from pydantic import Field

import pint
ureg = pint.UnitRegistry()

class Beam(H5Group):
    energy: float = Field(ge=0, doc="X-Ray beam energy", unit=ureg.joule)
    distance: H5Int32 = Field(ge=0, 
                                  doc="Distance from sample to detector", 
                                  unit=ureg.millimeter)

beam = Beam(energy=3.4, distance=7500)
