Tutorial
========

This tutorial won't really go into all the details one needs to know,
but it should be able to help people get started. This tutorial
assumes some fundamental knowledge about Python and HDF5.

A convention to follow is to create your h5pydantic models in a
``model.py`` file.

The motivation for h5pydantic was a Synchrotron use case, so
this tutorial will use a greatly simplified Synchrotron use case.

Specifying the Model
--------------------

To get started, some imports:

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
options, h5pydantic supports these through extra arguments passed to
the class. We've added a per acquisition metadata "beamstop" to the
acquisition. 

We now have all the bits and pieces to create our entire experiment:

.. literalinclude:: src/model.py
  :pyobject: Experiment

which introduces our first container type, a list of Acquisitions;
which gets mapped to HDF5 groups indexed by number e.g. /data/0,
data/1 etc.

Using the Model
---------------

Now, lets use the model. In a real experiment the data would come from
your beamline, for this example we'll just use example values.

.. literalinclude:: src/dump.py
  :end-before: dump

Now, we're ready to dump this experiment to a file, there's a lot
going on in this snippet. We begin by creating a :meth:`h5pydantic.H5Group.dumper`
context manager, this will open the output file ``experiment.pdf`` at
the start of the context block, users can then write to the Datasets using
the h5py array assignment, at the end of the block h5pydantic will
close the output file.

.. literalinclude:: src/dump.py
  :start-at: experiment.dump

Our example experiment hdf file is now created, an ascii form of it is
as follows (the output of a call to h5dump):

.. literalinclude:: src/experiment.txt

Now, when it comes to analysis, we want to load up the HDF5 file from
disk. We use a context manager :meth:`h5pydantic.H5Group.load` that will open the
``experiment.hdf`` file, allow users to access all the data, including
datasets within the context block, and close the file at the end of
the context block.

.. literalinclude:: src/load.py
