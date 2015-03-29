fumi
====

A small and (hopefully) simple deployment tool.

fumi fetches deployment configurations from a `fumi.yml` file. To start using fumi in a project, simply create that file (either manually or with fumi).

Installation
------------

Soon

Usage
-----

```
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
```

Creating a new deployment configuration
---------------------------------------

You can let fumi create a blank configuration for you with all the mandatory fields by running:

```shell
fumi new CONF_NAME
```

Or you could just write it from scratch. It's a very simply yaml file, promise ;)

Deploying with a given configuration
------------------------------------

Once you have at least one configuration, you can deploy by running:

```shell
fumi deploy CONF_NAME
```

Or, if you have a default configuration set:

```shell
fumi deploy
```

Documentation
-------------

Soon
