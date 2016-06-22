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

"""This file contains the implementation of the ``prepare`` "deployment"."""

import datetime
import os
import scp
import tarfile

from fumi import util


def prepare(deployer):
    """Test connection and prepare directories.

    Arguments:
        deployer (``Deployer``): Deployer instance.

    Returns:
        Boolean indicating result of the preparation.
    """
    # SSH connection
    util.cprint('> Connecting to %s as %s...' % (
        deployer.host, deployer.user), 'cyan')

    status, ssh = util.connect(deployer)
    if not status:
        return False

    util.cprint('Connected!\n', 'green')


    # Directory structures
    util.cprint('> Checking remote directory structures...', 'cyan')

    status = util.check_dirs(ssh, deployer)
    if not status:
        return False

    util.cprint('Correct!\n', 'green')


    util.cprint('Preparation complete!', 'green')
    util.cprint('Make sure to upload shared files before deploying', 'white')

    # Close SSH connection
    ssh.close()

    return True
