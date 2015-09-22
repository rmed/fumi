# Quickstart

This section covers the (fast) setup of a deployment configuration and the
deployment of your project using that configuration. Check the [installation
section](index.md#installation) for installation instructions.

## Commands

*fumi* offers a small amount of easy to use commands:

- **deploy**: deploy with a given configuration
- **list**: show all the available configurations
- **new**: create a new deployment configuration with the bare minimum
- **remove**: remove an existing configuration.

You will most likely be using `deploy` the most, so you just need to remember
that you can use it in two ways:

By simply running:

    $ fumi deploy

in your project's directory, which will use the default configuration, or ask
you for a default one.


Or by running:

    $ fumi deploy CONF

where `CONF` is the configuration name that you want *fumi* to use.

---

## Creating your first configuration

In order to create a basic configuration with the bare minimum:

    $ fumi new CONF

This will create a `CONF` configuration in the `fumi.yml` file that you can
adapt to your project's needs. However, you should take a look at the
[structure of the deployment file](deployment_file.md) for advanced options and
details.

---

## Making your first deployment

Once you are happy with your configuration, run:

    $ fumi deploy CONF

to make your first deployment. Remember that you can also set it as default by
running:

    $ fumi deploy

and specifying the configuration to use by default.

---

## The deployment directory

The remote deployment directory has the following structure:

    deploy_dir/
        current/
            YOUR_PROJECT_FILES
        rev/
            20150329183900/
                YOUR_PROJECT_FILES

Each time you deploy your project, a new revision will be created in the `rev`
directory, using timestamp of the deployment as name. This directory is then
*symlinked* to the `current` directory, which is were the live version of your
project can be accessed from.

---

## Things to consider

*fumi* performs deployments through SSH. Since version 0.3.0, it is possible to
specify a password for the connection in the configuration file or introduce it
when deploying. Public key authentication is also available.

The tool is language-agnostic, hence it is up to you to decide how your project
must be deployed and what commands to execute in the remote host (or locally)
before and after deployment.

You will not be prompted for superuser password if you issue a *sudo* command
or similar.
