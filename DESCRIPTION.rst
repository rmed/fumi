fumi |PyPI version|
===================

A small and (hopefully) simple deployment tool.

fumi fetches deployment configurations from a ``fumi.yml`` file. To
start using fumi in a project, simply create that file (either manually
or with fumi).

Installation
------------

::

    $ pip install fumi

Documentation
-------------

Documentation is available online at http://fumi.readthedocs.org.

You may also build the documentation using MkDocs:

.. code:: shell

    $ mkdocs build

Usage
-----

::

    usage: fumi [-h] [--version] {deploy,list,new,remove} ...

    Simple deployment tool

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit

    commands:
      {deploy,list,new,remove}
        deploy              deploy with given configuration
        list                list all the available deployment configurations
        new                 create new deployment configuration
        remove              remove a configuration from the deployment file

.. |PyPI version| image:: https://img.shields.io/pypi/v/fumi.svg
   :target: https://pypi.python.org/pypi/fumi
