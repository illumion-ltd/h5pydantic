Tutorial
========

This tutorial won't really go into all the details one needs to know,
but it should be able to help people get started. This tutorial
assumes some fundamental knowledge about Python.

A convention to follow is to create your h5pydantic models in a
"model.py" file.

The motivational case for h5pydantic was a Synchrotron use case, so
this tutorial will use a greatly simplified Synchrotron use case.

Specifying the Model
--------------------

To get started, import H5Dataset and H5Group from h5pydantic:

.. literalinclude:: src/model.py
  :end-before: class

Now, lets define a baseline measurement of our beamline:

.. literalinclude:: src/model.py
  :pyobject: Baseline

Attributes of atomic types are stored as HDF5 attributes.

Next, lets have two baseline measurements:

.. literalinclude:: src/model.py
  :pyobject: Metadata

Now, lets take some experimental measurements:

.. literalinclude:: src/model.py
  :pyobject: Acquisition

H5Datasets map directly to HDF5 datasets, which can have a lot of
options, h5pydantic supports these through attributes that start with
underscores. We've added a per acquisition metadata "beamstop" to the
acquisition. 

We now have all the bits and pieces to create our entire experiment:

.. literalinclude:: src/model.py
  :pyobject: Experiment

which introduces our first container type, a list of Acquisitions.

Using the Model
---------------

Now, lets use the model. In a real experiment the data would come from
your beamline, for this example we'll just use example values.

.. literalinclude:: src/dump.py
  :end-before: dump

Note the use of the _data attribute, which we use to set the data of our detector,
here we're using random arrays.

Now, we're ready to save this experiment to a file, using the Python convention of calling this :ref: dump()

.. literalinclude:: src/dump.py
  :start-at: experiment.dump

Our example experiment will have a HDF5 file layout as follows::

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

.. literalinclude:: src/load.py
