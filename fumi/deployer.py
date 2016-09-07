# -*- coding: utf-8 -*-
#
# fumi deployment tool
# https://github.com/rmed/fumi
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Code for the ``Deployer`` class, which acts as proxy for configurations."""

import gettext
import types

from fumi import messages as m
from fumi import deployments
from fumi.util import cprint


class Deployer(object):
    """Configuration parsed from the ``fumi.yml`` file.

    Attributes:
        source_type (str): Source type (e.g. 'local' or 'git'). Required.
        source_path (str): Path to the source files in local machine. Required.
        host (str): Host to perform the deployment in. Required.
        user (str): User to use for the deployment. Required.
        use_password (bool): Whether or not to use password. If set to ``False``
            (default), will rely on public key authentication. Otherwise, it
            will be asked for during deployment or may be configured through the
            ``password`` attribute.
        password (str): If ``use_password`` is set to True, this attribute can
            be used to specify the password used for the connection. Otherwise
            it will be asked for during deployment.
        deploy_path (str): Remote host path in which to deploy files. Required.
        predep (list[str]): List of commands to execute before deploying.
        postdep (list[str]): List of commands to execute after deploying.
        host_tmp (str): In ``local`` deployments, the remote directory to use
            for uploading the compressed files (defaults to ``'/tmp'``).
        keep_max (int): Maximum revisions to keep in the remote server.
        local_ignore (list[str]): List of files (or directories) to ignore in
            ``local`` deployments.
        buffer_size (int): Buffer size (in bytes) for file copying in ``local``
            deployments. Defaults to 1 MB.
        shared_paths (list[str]): List of file and directory paths that
            should be shared accross deployments. These are relative to the
            root of the project and are linked to the current revision.
    """

    def __init__(self, **kwargs):
        # Source information
        self.source_type = kwargs['source-type']
        self.source_path = kwargs['source-path']

        # Destination host information
        self.host = kwargs['host']
        self.user = kwargs['user']
        self.use_password = kwargs.get('use-password', False)
        self.password = kwargs.get('password')
        self.deploy_path = kwargs['deploy-path']

        # Pre-deployment commands
        predep = kwargs.get('predep', [])
        self.predep = []

        for p in predep:
            # Single key dicts
            for k, v in p.items():
                self.predep.append((k, v))

        # Post-deployment commands
        postdep = kwargs.get('postdep', [])
        self.postdep = []

        for p in postdep:
            # Single key dicts
            for k, v in p.items():
                self.postdep.append((k, v))


        # Optional information
        self.host_tmp = kwargs.get('host-tmp', '/tmp')
        self.keep_max = kwargs.get('keep-max')
        self.local_ignore = kwargs.get('local-ignore')
        self.buffer_size = int(kwargs.get('buffer-size', 1024 * 1024))
        self.shared_paths = kwargs.get('shared-paths', [])

def build_deployer(config):
    """Build a Deployer object.

    Arguments:
        config (dict): Parsed section of the YAML configuration file.

    Returns:
        Boolean indicating result and ``Deployer`` instance or ``None``.
    """
    try:
        deployer = Deployer(**config)

    except KeyError as e:
        # Missing required parameter
        key = e.args[0]
        cprint(m.DEP_MISSING_PARAM + '\n' % key, 'red')
        return False, None

    # Determine deployment function to use
    if deployer.source_type == 'local':
        cprint(m.DEP_LOCAL)
        deployer.deploy = types.MethodType(deployments.deploy_local, deployer)

    elif deployer.source_type == 'git':
        cprint(m.DEP_GIT)
        deployer.deploy = types.MethodType(deployments.deploy_git, deployer)

    else:
        # Unknown deployment type
        cprint(m.DEP_UNKNOWN % deployer.source_type, 'red')
        return False, None

    # Additional method for preparing/testing the deployment
    deployer.prepare = types.MethodType(deployments.prepare, deployer)

    return True, deployer
