Optional configuration fields
=============================

These fields are optional, but may be helpful in some cases.

buffer-size
-----------

``Integer``

Default: ``1048576`` (1 MB)

Buffer size (**in bytes**) to use when transmitting files over SSH in ``local``
deployments.

.. versionadded:: 0.4.0

default
-------

``Boolean``

Including this field in a configuration will allow you to run ``fumi deploy``
without specifying a configuration name. If you choose to specify it manually,
add the following to any configuration:

.. code-block:: yaml

    default: true

.. note::

    Fumi will obtain the list of configurations alphabetically, so take that
    into account if you write the field in several configurations.

host-tmp
--------

``String``

Default: ``/tmp/``

Absolute path to the directory in which the compressed file will be uploaded
to in ``local`` deployments.

local-ignore
------------

``List``

Use this field if you are performing a ``local`` deployment to exclude files
and/or directories when compressing the source. For instance, this is how this
field would look like for a project such as fumi:

.. code-block:: yaml

    local-ignore:
        - .git
        - .gitignore
        - docs
        - build
        - dist
        - fumi.yml


This way, directories ``.git``, ``docs``, ``build``, ``dist`` and files
``.gitignore``, ``fumi.yml`` will not be added to the compressed file.

keep-max
--------

``Integer``

Maximum number of revisions to keep in the ``rev`` directory. After deploying,
fumi will check this number, if present, and purge remote revisions until the
maximum number of revisions remains.

password
--------

``String``

Password to use when connecting to the server. Note that if ``use-password``
is set to ``true`` and you do not provide a password (e.g. so it is not
included in version control), you will be asked for the password in each
deployment.

.. warning::

    The password is stored as **plaintext**. You should either introduce the
    password in each deployment or use **public key authentication**.

.. versionadded:: 0.3.0

postdep
-------

``List``

Post deployment commands. These commands are executed after the source has
been uploaded/cloned in the remote host and linked to the ``current``
directory. Here is an example for a ruby on rails application:

.. code-block:: yaml

    postdep:
        - remote: 'bundle install'
        - remote: 'rake db:migrate'
        - local: 'scp my_secret_config.rb myuser@myhost:/home/app/current'
        - remote: 'touch tmp/restart.txt'

The order in this list will be preserved at the time of execution, so it is
possible to alternate between local and remote commands easily.

.. note::

    Local commands are executed **relative to the current working directory**,
    while remote commands are executed **relative to the current revision
    directory** (``current``).

.. note::

    Following YAML convention, **the command should be escaped with single
    quotes in order to parse it as a raw string**.

predep
------

``List``

Pre deployment commads. These commads are executed prior to uploading/cloning
the source in the remote server. This field has a structure similar to:

.. code-block:: yaml

    predep:
        - local: 'rm db/development.sql'
        - local: 'rm db/schema.rb'
        - remote: 'service apache stop'

The order in this list will be preserved at the time of execution, so it is
possible to alternate between local and remote commands easily.

.. note::

    Local commands are executed **relative to the current working directory**,
    while remote commands are executed **relative to the remote user's home
    directory** (``~/``).

.. note::

    Following YAML convention, **the command should be escaped with single
    quotes in order to parse it as a raw string**.

shared-paths
------------

``List``

List of file and directory paths that should be shared accross deployments.
These are relative to the root of the project and are linked to the current
revision after each deployment.

An example of this would be linking configuration files that were not included
in version control:

.. code-block:: yaml

    shared-paths:
        - instance/production.conf
        - instance/private_key

.. versionadded:: 0.4.0

use-password
------------

``Boolean``

Default: ``false``

Indicates whether a password will be used to connect or not. If this field is
not present (value ``false``), fumi will rely on public key authentication.

If the field is set to ``true``, then you may either specify the password in
the ``password`` field or manually introduce it when deploying.

.. versionadded:: 0.3.0
