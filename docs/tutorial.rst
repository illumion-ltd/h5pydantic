Tutorial
========

This tutorial won't really go into all the details one needs to know,
but it should be able to help people get started. This tutorial
assumes some fundamental knowledge about Python.

A convention to follow is to create your h5pydantic models in a
"models.py" file.

The motivational case for h5pydantic was a Synchrotron use case, so
this tutorial will use a greatly simplified Synchrotron use case.

Specifying the Model
====================

... sample.py: Python
from h5pydantic import H5Dataset, H5Group

To get started, import H5Dataset and H5Group from h5pydantic

Now, lets define a baseline measurement of our beamline:
... sample.py: Python

class Baseline(H5Group):
    temperature: float
    humidity: float

Attributes of atomic types are stored as HDF5 attributes.

Next, lets have two baseline measurements:

...sample.py: Python

class Metadata(H5Group):
    start: Baseline
    end: baseline

Now, lets take some experimental measurements:
...sample.py: Python

class Acquisition(H5Dataset):
   _shape = (1024, 1024)
   _dtype = "int32"
   beamstop: int

H5Datasets map directly to HDF5 datasets, which can have a lot of
options, h5pydantic supports these through attributes that start with
underscores. We've added a per acquisition metadata "beamstop" to the
acquisition. 

We now have all the bits and pieces to create our entire experiment:

...sample.py Python

class Experiment:
    metadata: Metadata
    data: list[Acquisition]

which introduces our first container type a list of Acquisitions.

Using the Model
===============

Now, lets use the model. In a real experiment the data would come from
your beamline, for this example we'll just use example values.

... experiment
from model import 

experiment = Experiment(metadata.start = {"temperature" : 25.0, "humidity": 0.4},
                        metadata.end = {"temperature": 26.0, "humidity": 0.4},
			data = [{_data = numpy.array.randint(255), beamstop=10},
                                {_data = numpy.array.randint(255), beamstop=11},
				{_data = numpy.array.randint(255), beamstop=12}])

Note the use of the _data attribute, which we use to set the data of our detector,
here we're using random arrays.

Now, we're ready to save this experiment to a file, using the Python convention of calling this :ref: dump()

... saving: Python

experiment.dump(Path("experiment.hdf"))

Our example experiment will have a HDF5 file layout as follows:

...hdf5 layout:
/metadata/start/temperature
/metadata/start/humidity
/metadata/end/temperature
/metadata/end/humidity
/data/0/[dataset]
/data/0/beamstop
/data/1/[dataset]
/data/1/beamstop
/data/2/[dataset]
/data/2/beamstop

Now, when it comes to analysis, we want to load up the HDF5 file from disk:

...hdf5 analysis: Python
from model import Experiment
from pathlib import Path

experiment = Experiment.load(Path("experiment.hdf"))

data1 = experiment.data[1]._data
starting_temp = experiment.metadata.start.temperature



