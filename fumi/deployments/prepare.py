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

"""Implementation of the ``prepare`` "deployment".

This is simply used to check connection configuration and create the remote
directory tree structure.
"""

from fumi import messages as m
from fumi import util


def prepare(deployer):
    """Test connection and prepare directories.

    Arguments:
        deployer (``Deployer``): Deployer instance.

    Returns:
        Boolean indicating result of the preparation.
    """
    # SSH connection
    util.cprint(
        '> ' + m.DEP_CONNECTING % (deployer.host, deployer.user),
        'cyan'
    )

    status, ssh = util.connect(deployer)
    if not status:
        ssh.close()
        return False

    util.cprint(m.DEP_CONNECTED + '\n', 'green')


    # Directory structures
    util.cprint('> ' + m.DEP_CREATEDIR, 'cyan')

    status = util.create_dirs(ssh, deployer)
    if not status:
        ssh.close()
        return False

    util.cprint(m.CORRECT + '\n', 'green')


    util.cprint(m.DEP_PREPARE_COMPLETE, 'green')
    util.cprint(m.DEP_PREPARE_NOTICE, 'white')

    # Close SSH connection
    ssh.close()

    return True
