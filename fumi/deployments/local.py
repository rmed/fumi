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

"""This file contains the implementation of the ``local`` deployment."""

import datetime
import os
import scp
import tarfile

from fumi import util


def deploy(deployer):
    """Local based deployment.

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


    # Compress source to temporary directory
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    compressed_file = timestamp + '.tar.gz'
    tmp_local = os.path.join('/tmp', compressed_file)

    if deployer.local_ignore:
        cnt_list = list(
            set(os.listdir(deployer.source_path))^set(deployer.local_ignore))

    else:
        cnt_list = os.listdir(deployer.source_path)

    util.cprint('> Compressing source to %s' % tmp_local, 'cyan')

    with tarfile.open(tmp_local, "w:gz") as tar:
        for item in cnt_list:
            path = os.path.join(deployer.source_path, item)

            if os.path.exists(path):
                # Compress
                tar.add(path, arcname=timestamp + '/' + item)

            else:
                # Ignore
                util.cprint('Path "%s" does not exist, ignoring' % path, 'white')

    util.cprint('Done!\n', 'green')


    # Upload compressed source
    util.cprint('> Uploading %s...' % compressed_file, 'cyan')

    try:
        uload = scp.SCPClient(
            ssh.get_transport(),
            buff_size=deployer.buffer_size)

    except:
        # Failed to initiate SCP
        util.cprint('Failed to initiate SCP, check configuration', 'red')
        status = util.rollback(ssh, deployer, timestamp, 1)
        return False

    uload_tmp = deployer.host_tmp or '/tmp'
    uload_path = os.path.join(uload_tmp, compressed_file)

    try:
        uload.put(tmp_local, uload_path)

    except scp.SCPException as e:
        util.cprint('Error uploading to server: %s\n' % e, 'red')
        status = util.rollback(ssh, deployer, timestamp, 3)
        return False

    util.cprint('Done!\n', 'green')


    # Uncompress source to deploy_path/rev
    util.cprint('> Uncompressing remote file...', 'cyan')

    rev_path = os.path.join(deployer.deploy_path, 'rev')
    untar = 'tar -C %s -zxvf %s' % (rev_path, uload_path)

    stdin, stdout, stderr = ssh.exec_command(untar)
    status = stdout.channel.recv_exit_status()

    if status == 127:
        util.cprint('Error: tar command not found in remote host\n', 'red')

        status = util.rollback(ssh, deployer, timestamp, 1)
        return False

    elif status == 1:
        util.cprint('Error: some files differ\n', 'red')
        util.cprint(*stderr.readlines())

        status = util.rollback(ssh, deployer, timestamp, 2)
        return False

    elif status == 2:
        util.cprint('Fatal error when extracting remote file', 'red')
        util.cprint(*stderr.readlines())

        status = util.rollback(ssh, deployer, timestamp, 2)
        return False

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


    # Link shared paths
    util.symlink_shared(ssh, deployer)


    # Clean revisions
    if deployer.keep_max:
        status = util.clean_revisions(ssh, deployer.keep_max, rev_path)


    # Cleanup temporary files
    util.cprint('> Cleaning temporary files...', 'cyan')

    util.remove_local(tmp_local)
    util.remove_remote(ssh, uload_path)

    util.cprint('Done!\n', 'green')


    util.cprint('Deployment complete!', 'green')

    # Close SSH connection
    ssh.close()

    return True
