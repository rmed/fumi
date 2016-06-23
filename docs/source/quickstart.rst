Quickstart
==========

This section covers the basic setup of a deployment configuration and the
deployment process using that configuration.

Commands
--------

The following commands are available in fumi:

- ``deploy``: deploy using a specific configuration
- ``list``: show all available configurations
- ``new``: create a new deployment configuration (minimum structure)
- ``prepare``: test connection and prepare remote directories
- ``remove`` remove an existing configuration

You can also run::

    fumi -h

To obtain help for each command.


Creating your first configuration
---------------------------------

In order to create a basic configuration::

    fumi new CONF_NAME

This will create a ``CONF_NAME`` configuration in the ``fumi.yml`` file that
you can adapt to your needs. However, you should take a look at the structure
of the deployment file for advanced options and details (check
:doc:`deployment_file`).


Making your first deployment
----------------------------

Once you are happy with your configuration, you may test connection running::

    fumi prepare CONF_NAME

to make sure everything works and create the remote directories. At this point,
you may wish to upload any shared files before deploying.

In order to deploy, run::

    fumi deploy CONF_NAME

You can also set a default configuration to use by running::

    fumi deploy

and specifying the configuration to use by default.


The deployment directory
------------------------

The remote deployment directory has the following structure::

    deploy_dir/
        current/
            YOUR_PROJECT_FILES
        rev/
            20150329183900/
                YOUR_PROJECT_FILES
        shared/
            SHARED_FILES

Each time you deploy your project, a new revision is created in the ``rev``
directory using the timestamp of the deployment as name. This directory is then
*symlinked* to the ``current`` directory, which is where the latest revision of
your project can be accessed from.

If configured, the specified files and directories in the ``shared`` directory
will also be *symlinked* to the ``current`` directory.


Things to consider
------------------

Deployments are performed through SSH. Since **version 0.3.0**, it is possible
to specify a password for the connection in the configuration file or introduce
it manually when deploying, although public key authentication is recommended.

It is up to you to determine how your project must be deployed and what
commands have to be executed in both local and remote machines before and after
deployment.

.. warning::

    You will not be prompted for superuser password if you issue a sudo
    command or similar.
