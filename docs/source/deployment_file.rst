Deployment file
===============

The deployment file is named ``fumi.yml`` and should be located in the root
directory of your project. This file follows standard YAML syntax, so it should
be easy to modify manually.


A basic deployment file
-----------------------

A basic ``fumi.yml`` file has the following structure:

.. code-block:: yaml

    chibi:
        source-type: local
        source-path: .

        host: myhost.com
        user: fumi
        deploy-path: /home/myapp

Here, we specify that we want to upload our project from a local directory
(which happens to be the directory that contains the ``fumi.yml`` file), that
our remote server can be accessed from ``myhost.com`` with user ``fumi`` and
the deployment directory to use in the remote host.

Of course, you may have as many deployment configurations as you want:

.. code-block:: yaml

    chibi:
        source-type: local
        source-path: .

        host: myhost.com
        user: fumi
        deploy-path: /home/myapp

    wuzhang:
        source-type: git
        source-path: http://my-repo.git

        host: mysecondhost.com
        user: fumi
        deploy-path: /home/app


Configuration fields
--------------------

You can check the following sections for more information on each configuration
field.

.. toctree::
   :maxdepth: 2

   fields_required
   fields_optional
