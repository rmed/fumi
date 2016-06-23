Required configuration fields
=============================

These fields have to be present for deployment to be possible.


deploy-path
-----------

``String``

Absolute path to the deployment directory in the remote host.

host
----

``String``

The remote host that fumi must connect to. **SSH must be enabled**.

source-type
-----------

``String``

Used to determine which basic actions must be performed in order to deploy
the project. Available types are:

- ``local``: compress a local directory and upload it to the server through SSH
- ``git``: clone a git repository directly in the remote server

source-path
-----------

``String``

Tells fumi where to get the files of the project from. Depending on the
``source-type``:

- ``local``: local directory in which the source can be found (usually
specifying the root directory with ``.`` is enough)
- ``git``: git url needed for the ``git clone URL`` command that will be
executed in the remote host

user
----

``String``

User that fumi will log in as in order to perform deployments. You may want
to create a special user for this, just in case.
