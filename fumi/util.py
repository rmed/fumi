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

"""Utility code for fumi.

These are common functions used in different deployments.
"""

from __future__ import print_function

import blessings
import getpass
import gettext
import os
import paramiko
import shutil
import subprocess
import yaml

from fumi import messages as m

COLOR_TERM = blessings.Terminal()


def check_dirs(ssh, deployer):
    """Check if all the necessary directories exist in the remote host.

    Arguments:
        ssh: Established SSH connection instance.
        deployer (``Deployer``): Deployer instance.

    Returns:
        Boolean indicating result.
    """
    # Remote temporary
    if not dir_exists(ssh, deployer.host_tmp):
        cprint(m.REMOTE_TMP_NOEXIST, 'red')
        return False

    # Deployment path
    if not dir_exists(ssh, deployer.deploy_path):
        cprint(m.REMOTE_DEP_NOEXIST, 'red')
        return False

    # Revisions
    rev = os.path.join(deployer.deploy_path, 'rev')
    if not dir_exists(ssh, rev):
        cprint(m.REMOTE_REV_NOEXIST, 'red')
        return False

    # Shared files
    shared = os.path.join(deployer.deploy_path, 'shared')
    if not dir_exists(ssh, shared):
        cprint(m.REMOTE_SHR_NOEXIST, 'red')
        return False

    return True

def create_dirs(ssh, deployer):
    """Create remote directories.

    Arguments:
        ssh: Established SSH connection instance.
        deployer (``Deployer``): Deployer instance.

    Returns:
        Boolean indicating result.
    """
    # Remote temporary
    if deployer.host_tmp != '/tmp' and not create_tree(ssh, deployer.host_tmp):
        cprint(m.REMOTE_TMP_CREATE_ERR, 'red')
        return False

    # Deployment path
    if not create_tree(ssh, deployer.deploy_path):
        cprint(m.REMOTE_DEP_CREATE_ERR, 'red')
        return False

    # Revisions
    rev = os.path.join(deployer.deploy_path, 'rev')
    if not create_tree(ssh, rev):
        cprint(m.REMOTE_REV_CREATE_ERR, 'red')
        return False

    # Shared files
    shared = os.path.join(deployer.deploy_path, 'shared')
    if not create_tree(ssh, shared):
        cprint(m.REMOTE_SHR_CREATE_ERR, 'red')
        return False

    return True

def connect(deployer):
    """Try to connect to the remote host through SSH.

    Arguments:
        dep (``Deployer``): Deployer instance.

    Returns:
        Boolean indicating result and paramiko.SSHClient instance or ``None``.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if not deployer.use_password:
        # Not using password, rely on public key authentication
        try:
            cprint(m.CONN_PUBKEY + '\n', 'magenta')
            ssh.connect(deployer.host, username=deployer.user)

        except paramiko.ssh_exception.AuthenticationException:
            cprint(m.CONN_AUTH_FAIL, 'red')
            return False, None

        except paramiko.ssh_exception.PasswordRequiredException:
            cprint(m.CONN_KEYPASS, 'red')
            return False, None

        except Exception as e:
            # Unknown exception
            cprint(m.UNEXPECTED_ERR % e, 'red')
            return False, None

    elif deployer.use_password and not deployer.password:
        # Using password but not supplied in the yml file, ask for it
        cprint(m.CONN_NEEDPASS + '\n', 'magenta')
        pwd = getpass.getpass(m.CONN_PASS)

        try:
            ssh.connect(deployer.host, username=deployer.user, password=pwd)

        except:
            cprint(m.CONN_FAIL, 'red')
            return False, None

    elif deployer.use_password and deployer.password:
        # Using password supplied in the yml file
        cprint(m.CONN_TRYPASS + '\n' , 'magenta')

        try:
            ssh.connect(
                deployer.host,
                username=deployer.user,
                password=deployer.password)

        except:
            cprint(m.CONN_FAIL, 'red')
            return False, None

    return True, ssh

def clean_revisions(ssh, keep_max, rev_path):
    """Remove old revisions from the remote server.

    Only the most recent revisions will be kept.

    Arguments:
        ssh: Established SSH connection instance.
        max_keep (int): Maximum number of revisions to keep.
        rev_path (str): Path to the revisions directory in remote host.

    Returns:
        Boolean indicating result.
    """
    cprint('> ' + m.REV_CHECK, 'cyan')

    stdin, stdout, stderr = ssh.exec_command('ls %s' % rev_path)
    status = stdout.channel.recv_exit_status()

    if status == 1 or status == 2:
        cprint(m.REV_LIST_ERR, 'red')
        cprint(*stderr.readlines())
        return False

    revisions = stdout.readlines()

    if len(revisions) > keep_max:
        old_revisions = []

        while len(revisions) > keep_max:
            old_revisions.append(revisions.pop(0))

        for r in old_revisions:
            cprint(m.REV_RM % r.strip(), 'magenta')
            rm_old = 'rm -rf %s' % os.path.join(rev_path, r.strip())
            stdin, stdout, stderr = ssh.exec_command(rm_old)

    cprint(m.DONE +'\n', 'green')
    return True

def create_tree(ssh, path):
    """Try to create a remote tree path.

    Arguments:
        ssh: Established SSH connection instance.
        path (str): Tree path to create.

    Returns:
        Boolean indicating whether the tree was created or not.
    """
    stdin, stdout, stderr = ssh.exec_command(
        "mkdir -p %s" % path)

    if stdout.channel.recv_exit_status() == 0:
        return True

    return False

def dir_exists(ssh, path):
    """Check whether a remote directory exists or not.

    Arguments:
        ssh: Established SSH connection instance.
        path (str): Path of the directory to check.

    Returns:
        Boolean indicating if the directory exists or not.
    """
    stdin, stdout, stderr = ssh.exec_command(
        "[ -d %s ] && echo OK" % path)

    result = stdout.read()

    if result:
        return True

    return False

def cprint(text, color='normal', bold=True):
    """Print the given text using blessings terminal.

    Arguments:
        text (str): Text to print.
        color (str): Color to print the message in.
        bold (bool): Whether or not the text should be printed in bold.
    """
    if color == 'cyan':
        to_print = COLOR_TERM.cyan(text)

    elif color == 'green':
        to_print = COLOR_TERM.green(text)

    elif color == 'magenta':
        to_print = COLOR_TERM.magenta(text)

    elif color == 'red':
        to_print = COLOR_TERM.red(text)

    elif color == 'white':
        to_print = COLOR_TERM.white(text)

    else:
        # Normal text
        to_print = text

    if bold and color != 'normal':
        print(COLOR_TERM.bold(to_print))

    else:
        print(to_print)

def read_yaml(path):
    """Reads the given YAML file.

    Arguments:
        path (str): Path to the file to read (fumi.yml).

    Returns:
        Boolean indicating result and ``dict`` with the information or ``None``.
    """
    if os.path.isfile(path):
        with open(path, 'r') as fumi_yml:
            try:
                content = yaml.load(fumi_yml)

            except yaml.YAMLError as e:
                cprint(m.YML_ERR % e, 'red')
                return False, None

        return True, content

    return True, None

def remove_local(path):
    """Remove a local file or directory.

    Arguments:
        path (str): Absolute path to the file or directory.

    Returns:
        Boolean indicating result.
    """
    if os.path.isfile(path):
        # Regular file
        remover = os.remove

    elif os.path.isdir(path):
        # Directory
        remover = shutil.rmtree

    else:
        # What?
        cprint(m.PATH_NOEXIST % path, 'red')
        return False

    try:
        remover(path)

    except Exception as e:
        # Something failed
        cprint(m.RM_ERR % (path, e), 'red')
        return False

    return True

def remove_remote(ssh, path):
    """Remove a remote file or directory.

    Arguments:
        ssh: Established SSH connection instance.
        path (str): Absolute path to the file or directory.

    Returns:
        Boolean indicating result.
    """
    stdin, stdout, stderr = ssh.exec_command('rm -rf %s' % path)

    return True

def rollback(ssh, deployer, timestamp, level):
    """Perform a rollback based on current deployment.

    Rollbacks have several levels:

        1. Remove locally generated files (compressed source).
        2. Remove uploaded compressed source (if any).
        3. Remove remote revision.
        4. Link previous revision.

    All the levels lower to the one provided are executed as well.

    Arguments:
        ssh: Established SSH connection instance.
        deployer (``Deployer``): Deployer instance.
        timestamp (str): Timestamp for the revision to rollback.
        level (int): Level of rollback to perform.

    Returns:
        Boolean indicating result of the rollback.
    """
    cprint('> ' + m.ROLLBACK_BEGIN, 'cyan')

    # Relevant names
    comp_file = timestamp + '.tar.gz'
    rev_path = os.path.join(deployer.deploy_path, 'rev')

    if level >= 1:
        # Remove local files
        local_file = os.path.join('/tmp', comp_file)

        if os.path.isfile(local_file):
            cprint(m.RM_MSG_LOCAL % local_file, 'magenta')

            try:
                os.remove(local_file)

            except:
                # Do not exit because of local file error, simply ignore
                cprint(m.RM_FAIL % local_file, 'red')
                pass

    if level >= 2:
        # Remove remote files
        uload_tmp = deployer.host_tmp or '/tmp'
        remote_file = os.path.join(uload_tmp, comp_file)

        # Check if file exists
        stdin, stdout, stderr = ssh.exec_command(
            '[ -f %s ] && echo OK' % remote_file)

        result = stdout.read()

        if result:
            # File exists
            cprint(m.RM_MSG_REMOTE % remote_file, 'magenta')

            stdin, stdout, stderr = ssh.exec_command(
                'rm %s' % remote_file)

            status = stdout.channel.recv_exit_status()

            if status < 0:
                # Could not remove it?
                cprint(m.RM_ERR_REMOTEF, 'red')
                cprint(*stderr.readlines())

        else:
            # File does not exist
            cprint(m.REMOTE_FILE_NOEXIST % remote_file, 'white')

    if level >= 3:
        # Remove revision
        stdin, stdout, stderr = ssh.exec_command(
            '[ -d %s ] && echo OK' % rev_path)

        result = stdout.read()

        if result:
            # Directory exists
            cprint(m.REV_RM_REMOTE % timestamp, 'magenta')

            stdin, stdout, stderr = ssh.exec_command(
                'rm -rf %s' % os.path.join(rev_path, timestamp))

            status = stdout.channel.recv_exit_status()

            if status < 0:
                cprint(m.RM_ERR_REMOTED, 'red')
                cprint(*stderr.readlines())

        else:
            # File does not exist
            cprint(m.REMOTE_REV_NOEXIST, 'white')

    if level >= 4:
        # Link previous version
        stdin, stdout, stderr = ssh.exec_command('ls %s' % rev_path)
        status = stdout.channel.recv_exit_status()

        revs = [r.rstrip() for r in stdout.readlines()]

        if timestamp in revs:
            revs.remove(timestamp)

        if len(revs) > 0:
            cprint(m.REV_LINK_PREV % revs[-1], 'magenta')

            link_path = os.path.join(deployer.deploy_path, 'current')
            previous_rev = os.path.join(deployer.deploy_path, 'rev', revs[-1])

            ln = 'ln -sfn %s %s' % (previous_rev, link_path)

            stdin, stdout, stderr = ssh.exec_command(ln)

        else:
            # No more revisions
            cprint(m.REV_PREV_MISSING, 'white')

    cprint(m.DONE, 'green')
    return True

def run_commands(ssh, commands, remote_path=None):
    """Execute pre and post deployment commands (both local and remote).

    Remote pre-deployment commands are usually executed in the user's
    directory (~/) when possible, while post-deployment commands are executed
    in the directory of the revision that has been deployed
    (deploy_path/current).

    Arguments:
        ssh: Established SSH connection instance.
        commands (list[str]): List of commands to execute (predep or postdep).
        remote_path (str): Remote path in which to execute commands.

    Returns:
        Boolean indicating result.
    """
    if not commands:
        # No commands to execute
        return True

    cprint('> ' + m.CMD_EXEC, 'cyan')

    popd = 'popd > /dev/null 2>&1'

    for cmd in commands:
        command_type = cmd[0]
        to_run = cmd[1]

        if command_type == 'local':
            cprint(m.CMD_LOCAL % to_run, 'magenta')

            subprocess.Popen(to_run, shell=True).wait()

        elif command_type == 'remote':
            cprint(m.CMD_REMOTE % to_run, 'magenta')

            if remote_path:
                # Only for post-deployment commands
                pushd = 'pushd %s > /dev/null 2>&1' % remote_path
                to_run = '%s; %s; %s' % (pushd, to_run, popd)

            stdin, stdout, stderr = ssh.exec_command(to_run)

            # Print command output in real-time
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    cprint(stdout.readline())

        else:
            # Unknown type, skip
            cprint((m.CMD_SKIP % command_type) + '\n', 'red')

    cprint(m.DONE + '\n', 'green')
    return True

def symlink(ssh, deployer, rev_path, timestamp):
    """Symlink the deployed revision to the deploy_path/current directory.

    Arguments:
        ssh: Established SSH connection instance.
        deployer (``Deployer``): Deployer instance.
        rev_path (str): Path to the revisions directory in remote host.
        timestamp (str): Timestamp that identifies current revision.

    Returns:
        Boolean indicating result.
    """
    cprint('> ' + m.LINK_DIR, 'cyan')

    link_path = os.path.join(deployer.deploy_path, 'current')
    current_rev = os.path.join(rev_path, timestamp)

    ln = 'ln -sfn %s %s' % (current_rev, link_path)

    stdin, stdout, stderr = ssh.exec_command(ln)
    # status = stdout.channel.recv_exit_status()

    cprint(m.DONE + '\n', 'green')
    return True

def symlink_shared(ssh, deployer):
    """Symlink shared files to the deploy_path/current directory.

    Arguments:
        ssh: Established SSH connection instance.
        deployer (``Deployer``): Deployer instance.

    Returns:
        Boolean indicating result.
    """
    if not deployer.shared_paths:
        # Nothing to link
        return True

    cprint('> ' + m.LINK_SHARED, 'cyan')

    current_path = os.path.join(deployer.deploy_path, 'current')
    shared_path = os.path.join(deployer.deploy_path, 'shared')

    for shared in deployer.shared_paths:
        cprint(m.LINKING % shared, 'magenta')

        src_path = os.path.join(shared_path, shared)
        dest_path = os.path.join(current_path, shared)

        ln = 'ln -sfn %s %s' % (src_path, dest_path)

        stdin, stdout, stderr = ssh.exec_command(ln)
        # status = stdout.channel.recv_exit_status()

    cprint(m.DONE + '\n', 'green')
    return True

def write_yaml(path, content):
    """Overwrite the content of the given YAML file.

    Arguments:
        path (str): Path to the file (fumi.yml).
        content (str): Content to write.

    Returns:
        Boolean indicating result.
    """
    with open(path, 'w') as fumi_yml:
        try:
            yaml.dump(content, fumi_yml, default_flow_style=False)

        except yaml.YAMLError as e:
            cprint(m.YML_WRITE_ERR % e, 'red')
            return False

    return True
