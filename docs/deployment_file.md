# Deployment file

The deployment file is named `fumi.yml` and should be located in the root directory of the project. This file follows standard YAML syntax, so it should not be too difficult to modify manually.

## A basic deployment file

A basic `fumi.yml` file will have a structure similar to this one:

```yaml
chibi:
    source-type: local
    source-path: .

    host: wu.site
    user: zhuge
    deploy-path: /home/yangtze
```

Here, we specify that we want to upload our project from a local directory (which happens to be the directory that contains `fumi.yml`), that our remote server can be accessed from `wu.site` with user `zhuge` and that the [deployment path](quickstart.md#the-deployment-directory).

Of course, you may have as many deployment configurations as you want:

```yaml
chibi:
    source-type: local
    source-path: .

    host: wu.site
    user: zhuge
    deploy-path: /home/yangtze

wuzhang:
    source-type: git
    source-path: http://my-repo.git

    host: wei.site
    user: sima
    deploy-path: /home/app
```

Following sections detail mandatory and optional fields for configurations.

## Mandatory fields

These fields must be present for *fumi* to work.

### source-type

The `source-type` is used to find which basic actions must be taken in order to get the project into the remote server. Available types are:

- **local**: compress local directory and upload it to server through SSH.
- **git**: clone a git repository directly in the remote server.

### source-path

The `source-path` is used to tell *fumi* where to get the project from. Depending on the `source-type`:

- **local**: local directory in which the source can be found (usuarlly specifying the current directory with `.` is enough).
- **git**: the git url needed for the `git clone URL` command to be executed in the server.

### host

The remote `host` that *fumi* must connect to. Make sure SSH is enabled!

### user

User that will be in charge of performing the deployments. You may want to create a special user for this, just in case.

### deploy-path

The directory that will contain current deployment and past revisions as detailed in the [deployment directory section](quickstart.md#the-deployment-directory).

## Optional fields

These fields are optional, but may be helpful in most cases.

### default

The `default` field will allow you to run `fumi deploy` without specifying a configuration name. If you choose to specify it manually, add the following to any configuration:

    default: true

Note that *fumi* will obtain the list of configurations alphabetically, so take that into account if you write the field in several configurations.

### host-tmp

By default, when using the `local` source type, the compressed source will be uploaded to `/tmp`. With this field you can specify the directory in which to upload the file instead.

### keep-max

Integer number that can be used to specify the maximum number of revisions to keep in the `rev` directory. After deploying, *fumi* will check this number and the number of revisions stored remotely and remove several of them until the maximum allowed is satisfied.

### predep

Pre-deployment commands. These commands are executed before uploading/cloning the source in the remote server. This field has a structure similar to:

```yaml
predep:
    local:
    - rm db/development.sql
    - rm db/schema.rb
    remote:
    - service apache stop
```

#### local

Commands to be executed in local machine. This field must be filled as an ordered list sorted by order of execution and are relative to the current directory.

#### remote

Commands to be executed in remote machine. Again, written as an ordered list and relative to the home folder of the user used to deploy.

### postdep

Post-deployment commands. These commands are executed after the source has been uploaded/cloned in the server and linked to the `current` directory. An usage example of this field would be when deploying a ruby on rails application:

```yaml
postdep:
    remote:
    - bundle install
    - rake db:migrate
    - touch tmp/restart.txt
```

#### local

Again commands executed in local machine relative to current directory.

#### remote

Commands executed in remote server **relative to directory of current deployment** (`current`)
