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

"""This file contains the implementation of the ``git`` deployment."""

import datetime
import os

from fumi import util


def deploy(deployer):
    """Git based deployment.

    Arguments:
        deployer (``Deployer``): Deployer instance.

    Returns:
        Boolean indicating result of the deployment.
    """
    # SSH connection
    util.cprint('> Connecting to %s as %s...' % (
        deployer.host, deployer.user), 'cyan')

    status, ssh = util.connect(deployer)
    if not status:
        return False

    util.cprint('Connected!\n', 'green')


    # Predeployment commands
    status, util.run_commands(ssh, deployer.predep)
    if not status:
        return False


    # Directory structures
    util.cprint('> Checking remote directory structures...', 'cyan')

    status = util.check_dirs(ssh, deployer)
    if not status:
        return False

    util.cprint('Correct!\n', 'green')


    # Clone source
    util.cprint('> Cloning repository...', 'cyan')

    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%Sr')
    rev_path = os.path.join(deployer.deploy_path, 'rev')
    current_rev = os.path.join(deployer.d_path, 'rev', timestamp)

    clone = 'git clone %s %s' % (deployer.s_path, current_rev)

    stdin, stdout, stderr = ssh.exec_command(clone)
    status = stdout.channel.recv_exit_status()

    if status == 127:
        util.cprint('git command not found in remote server')
        return False
    # TODO: check git exit codes

    util.cprint('Done!\n', 'green')


    # Link directory
    status = util.symlink(ssh, deployer, rev_path, timestamp)
    if not status:
        util.rollback(ssh, deployer, timestamp, 3)
        return False


    # Run post-deployment commands
    status = util.run_commands(
        ssh,
        deployer.postdep,
        os.path.join(deployer.deploy_path, 'current'))

    if not status:
        util.rollback(ssh, deployer, timestamp, 3)
        return False


    # Clean revisions
    if deployer.keep_max:
        status = util.clean_revisions(ssh, deployer.keep_max, rev_path)

    util.cprint('Deployment complete!', 'green')

    # Close SSH connection
    ssh.close()

    return True
