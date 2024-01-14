API Reference
=============

h5pydantic
----------

=========
Modelling
=========

For the most part, h5pydantic attempts to leave modelling to pydantic,
there are, of course, areas where the interaction is not seamless.

########
Optional
########

It is possible to type a field (which could be a Group, a Dataset, an
attribute, or a list) as typing.Optional. pydantic requires
that that this be done by assigning None to the field. I strongly
suggest using typing.Optional as well, for readability.

At this point, only typing.Optional Groups and Attributes are
supported. An Optional list[] does not make much sense, just leave the
list empty. Optional Datasets should be supported in future. 

#####
Lists
#####

h5pydantic will take a list[] type to mean a zero counted
group. An empty list is the only supported default value.

=========
Instances
=========

.. autoclass:: h5pydantic.H5Group
    :members:

.. autoclass:: h5pydantic.H5Dataset
    :members:
    :special-members: __getitem__, __setitem__

=====
Types
=====

.. automodule:: h5pydantic.models
    :members:

.. automodule:: h5pydantic.types
    :members:
