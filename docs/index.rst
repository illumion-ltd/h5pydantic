.. h5pydantic documentation master file, created by
   sphinx-quickstart on Fri May 12 18:37:20 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to h5pydantic's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Design:
 The h5pydantic project is designed to make it possible to specify a
 HDF5 file layout by specifying models through Python, in a similar
 way that Object Relation Mappers map from Python classes to SQL
 tables.

The project makes use h5py library to create and load HDF5 files, and
the pydantic library to handle creating Python models.

The name of the project comes from creating a portmanteau of
h5py and pydantic.

Roadmap:
 * Auto build documentation: I want the ability to produce
   documentation that describes the HDF5 file layout, without
   referencing the Python specification. Documentation strings of
   elements should flow through to the documentation.
 * Units: I want to fully support Pint units on all elements,
   including passing it through to documentation.
 * Hypothesis: I want to generate dump/load tests using Hypothesis.
 * Versioning: provide tool/guidance to support versioning of
   specifications, and loading of old formats.
 * Handle appendices data, e.g. user supplied sample environments,
   somehow, referenced? linked? external data sources?
 * Provide a traversal API or example to ease making exporters to
   other formats.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
