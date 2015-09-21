# -*- coding: utf-8 -*-
#
# fumi deployment tool
# https://github.com/rmed/fumi
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Rafael Medina García <rafamedgar@gmail.com>
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

from __future__ import print_function
from blessings import Terminal
import datetime
import getpass
import os
import paramiko
import scp
import subprocess
import sys
import tarfile

term = Terminal()


def deploy_local(deployment):
    """ Local based deployment. """
    cprint("> Connecting to %s as %s..." % (
        deployment.host, deployment.user), "cyan")

    ssh = _connect(deployment)
    cprint("Connected!\n", "green")

    _run_commands(ssh, deployment.predep)

    cprint("> Checking remote directory structures...", "cyan")
    _check_dirs(ssh, deployment)
    cprint("Correct!\n", "green")


    # Compress source to temporary directory
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    comp_file = timestamp + ".tar.gz"
    tmp_local = os.path.join("/tmp", comp_file)

    if deployment.local_ign:
        cnt_list = list(
            set(os.listdir(deployment.s_path))^set(deployment.local_ign))
    else:
        cnt_list = os.listdir(deployment.s_path)

    cprint("> Compressing source to /tmp/%s" % comp_file, "cyan")

    with tarfile.open(tmp_local, "w:gz") as tar:
        for item in cnt_list:
            tar.add(
                os.path.join(deployment.s_path, item),
                arcname=timestamp + "/" + item)

    cprint("Done!\n", "green")


    # Upload compressed source
    cprint("> Uploading %s..." % comp_file, "cyan")

    uload = scp.SCPClient(ssh.get_transport())
    uload_tmp = deployment.h_tmp or "/tmp"
    uload_path = os.path.join(uload_tmp, comp_file)

    try:
        uload.put(tmp_local, uload_path)

    except scp.SCPException as e:
        cprint("Error uploading to server: %s\n" % e, "red")
        _rollback(ssh, deployment, timestamp, 3)
        sys.exit()

    cprint("Done!\n", "green")


    # Uncompress source to deploy_path/rev
    cprint("> Uncompressing remote file...", "cyan")

    rev_path = os.path.join(deployment.d_path, "rev")
    untar = "tar -C %s -zxvf %s" % (rev_path, uload_path)

    stdin, stdout, stderr = ssh.exec_command(untar)
    status = stdout.channel.recv_exit_status()

    if status == 127:
        cprint("Error: tar command not found in remote host\n", "red")

        _rollback(ssh, deployment, timestamp, 1)
        sys.exit()

    elif status == 1:
        cprint("Error: some files differ\n", "red")
        print(*stderr.readlines())

        _rollback(ssh, deployment, timestamp, 2)
        sys.exit()

    elif status == 2:
        cprint("Fatal error when extracting remote file", "red")
        print(*stderr.readlines())

        _rollback(ssh, deployment, timestamp, 2)
        sys.exit()

    cprint("Done!\n", "green")


    # Link directory
    _symlink(ssh, deployment.d_path, rev_path, timestamp)


    # Run post-deployment commands
    _run_commands(ssh, deployment.postdep,
        os.path.join(deployment.d_path, "current"))


    # Clean revisions
    if deployment.keep:
        _clean_revisions(ssh, deployment.keep, rev_path)


    # Cleanup temporary files
    cprint("> Cleaning temporary files...", "cyan")

    subprocess.call(["rm", tmp_local])
    stdin, stdout, stderr = ssh.exec_command("rm %s" % uload_path)

    cprint("Done!\n", "green")


    cprint("Deployment complete!", "green")

def deploy_git(deployment):
    """ Git based deployment. """
    cprint("> Connecting to %s as %s..." % (
        deployment.host, deployment.user), "cyan")

    ssh = _connect(deployment)
    cprint("Connected!\n", "green")

    _run_commands(ssh, deployment.predep)

    cprint("> Checking remote directory structures...", "cyan")
    _check_dirs(ssh, deployment)
    cprint("Correct!\n", "green")


    # Clone source
    cprint("> Cloning repository...", "cyan")

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rev_path = os.path.join(deployment.d_path, "rev")
    current_rev = os.path.join(deployment.d_path, "rev", timestamp)
    clone = "git clone %s %s" % (deployment.s_path, current_rev)

    stdin, stdout, stderr = ssh.exec_command(clone)
    status = stdout.channel.recv_exit_status()

    if status == 127:
        sys.exit(term.bold_red("git command not found in remote server"))
    # TODO: check git exit codes

    cprint("Done!\n", "green")


    # Link directory
    _symlink(ssh, deployment.d_path, rev_path, timestamp)


    # Run post-deployment commands
    _run_commands(ssh, deployment.postdep,
        os.path.join(deployment.d_path, "current"))


    # Clean revisions
    if deployment.keep:
        _clean_revisions(ssh, deployment.keep, rev_path)


    cprint("Deployment complete!", "green")


def _check_dirs(ssh, dep):
    """ Check if all the necessary directories exist
        and the user has permission to write to them.
    """
    # Remote temporary
    if dep.h_tmp:
        if not _dir_exists(ssh, dep.h_tmp) and not _create_tree(ssh, dep.h_tmp):
            sys.exit(term.bold_red(
                "Cannot create remote temporary directory"))

    # Deployment path
    if not _dir_exists(ssh, dep.d_path) and not _create_tree(ssh, dep.d_path):
        sys.exit(term.bold_red(
            "Cannot create remote deployment directory"))

    # Revisions
    rev = os.path.join(dep.d_path, "rev")
    if not _dir_exists(ssh, rev) and not _create_tree(ssh, rev):
        sys.exit(term.bold_red(
            "Cannot create remote revisions directory"))

def _clean_revisions(ssh, keep, rev_path):
    """ Remove old revisions from the remote server.

        Only the most recent revisions will be kept, to a maximum defined
        by the keep argument.
    """
    cprint("> Checking old revisions...", "cyan")

    stdin, stdout, stderr = ssh.exec_command("ls %s" % rev_path)
    status = stdout.channel.recv_exit_status()

    if status == 1 or status == 2:
        print(*stderr.readlines())
        sys.exit(term.bold_red("Error obtaining list of revisions"))

    revisions = stdout.readlines()

    if len(revisions) > keep:
        old_revisions = []

        while len(revisions) > keep:
            old_revisions.append(revisions.pop(0))

        for r in old_revisions:
            cprint("Removing revision %s" % r.strip(), "magenta")
            rm_old = "rm -rf %s" % os.path.join(rev_path, r.strip())
            stdin, stdout, stderr = ssh.exec_command(rm_old)

    cprint("\nDone!\n", "green")

def _connect(deployment):
    """ Try to connect to the remote host through SSH using information from
        the provided Deployment object.

        returns a paramiko.SSHClient instance
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if not deployment.use_password:
        # Not using password, rely on public key authentication
        try:
            cprint("Trying to connect using public key\n", "magenta")
            ssh.connect(deployment.host, username=deployment.user)

        except:
            # May raise AuthenticationException or PasswordRequiredException
            cprint("Could not connect using public key", "red")
            sys.exit()

    elif deployment.use_password and not deployment.password:
        # Using password but not supplied in the yml file, ask for it
        cprint("Connection requires a password\n", "magenta")
        pwd = getpass.getpass("Password: ")

        try:
            ssh.connect(deployment.host,
                username=deployment.user, password=pwd)

        except:
            cprint("Could not connect, please check your credentials", "red")
            sys.exit()

    elif deployment.use_password and deployment.password:
        # Using password and supplied in the yml file
        cprint("Trying to connect using provided password\n", "magenta")

        try:
            ssh.connect(deployment.host,
                username=deployment.user, password=deployment.password)

        except:
            cprint("Could not connect, please check your credentials", "red")
            sys.exit()

    return ssh

def _create_tree(ssh, path):
    """ Try to create a remote tree path. """
    stdin, stdout, stderr = ssh.exec_command(
        "mkdir -p %s" % path)

    if stdout.channel.recv_exit_status() == 0:
        return True

    return False

def _dir_exists(ssh, directory):
    """ Check whether a remote directory exists or not. """
    stdin, stdout, stderr = ssh.exec_command(
        "[ -d %s ] && echo OK" % directory)

    result = stdout.read()

    if result:
        return True

    return False

def _rollback(ssh, dep, timestamp, level):
    """ Perform a rollback based on current deployment.

        Rollbacks have several levels:

        1 -> remove locally generated files (compressed source)
        2 -> remove uploaded compressed source (if any)
        3 -> remove remote revision
        4 -> link previous revision

        All the levels lower to the one provided are executed as well.
    """
    cprint("> Beginning rollback...", "cyan")

    comp_file = timestamp + ".tar.gz"
    rev_path = os.path.join(dep.d_path, "rev")

    if level >= 1:
        local_file = os.path.join("/tmp", comp_file)

        if os.path.isfile(local_file):
            cprint("Removing %s..." % local_file, "magenta")
            os.remove(local_file)

    if level >= 2:
        uload_tmp = dep.h_tmp or "/tmp"
        remote_file = os.path.join(uload_tmp, comp_file)

        stdin, stdout, stderr = ssh.exec_command(
            "[ -f %s ] && echo OK" % remote_file)

        result = stdout.read()

        if result:
            cprint("Removing remote file %s..." %
                remote_file, "magenta")
            stdin, stdout, stderr = ssh.exec_command(
                "rm %s" % remote_file)

            status = stdout.channel.recv_exit_status()

            if status < 0:
                cprint("Remote error", "red")
                sys.exit(*stderr.readlines())

    if level >= 3:
        stdin, stdout, stderr = ssh.exec_command(
            "[ -d %s ] && echo OK" % rev_path)

        result = stdout.read()

        if result:
            cprint("Removing remote revision %s..." %
                timestamp, "magenta")
            stdin, stdout, stderr = ssh.exec_command(
                "rm -rf %s" % os.path.join(rev_path, timestamp))

            status = stdout.channel.recv_exit_status()

            if status < 0:
                cprint("Remote error", "red")
                sys.exit(*stderr.readlines())

    if level >= 4:
        stdin, stdout, stderr = ssh.exec_command("ls %s" % rev_path)
        status = stdout.channel.recv_exit_status()

        revs = [r.rstrip() for r in stdout.readlines()]

        if timestamp in revs:
            revs.remove(timestamp)

        cprint("Linking previous revision %s..." %
            revs[-1], "magenta")

        link_path = os.path.join(dep.d_path, "current")
        ln = "ln -sfn %s %s" % (os.path.join(dep.d_path, "rev", revs[-1]),
            link_path)

        stdin, stdout, stderr = ssh.exec_command(ln)

    cprint("Done!", "green")

def _run_commands(ssh, commands, link_path=None):
    """ Execute pre and post deployment commands (both local and remote).

        Remote pre-deployment commands are usually executed in the user's
        directory (~/) when possible, while post-deployment commands are
        executed in the directory of the revision that has been deployed
        (deploy_path/current).
    """
    if not commands:
        return

    cprint("> Command execution", "cyan")
    for cmd in commands:
        k = list(cmd.keys())[0]

        if k == "local":
            to_run = cmd[k]
            cprint("Running local command: %s" % to_run, "magenta")

            subprocess.Popen(to_run, shell=True).wait()
            print("\n")

        elif k == "remote":
            to_run = cmd[k]

            # Only for post-deployment commands
            if link_path:
                to_run = "cd %s; %s" % (link_path, to_run)

            cprint("Running remote command: %s" % to_run, "magenta")

            stdin, stdout, stderr = ssh.exec_command(to_run)

            # Print command output in real-time
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    print(stdout.readline())

            print("\n")

        else:
            cprint("Uknown command: %s" % cmd, "red")
            print("\n")

    cprint("Done!\n", "green")


def _symlink(ssh, d_path, rev_path, timestamp):
    """ Symlink the deployed revision to the deploy_path/current
        directory.
    """
    cprint("> Linking directory...", "cyan")

    link_path = os.path.join(d_path, "current")
    current_rev = os.path.join(rev_path, timestamp)
    ln = "ln -sfn %s %s" % (current_rev, link_path)

    stdin, stdout, stderr = ssh.exec_command(ln)
    # status = stdout.channel.recv_exit_status()

    cprint("Done!\n", "green")

def cprint(text, color="white", bold=True):
    """ Print the given text using blessings terminal. """
    if color == "cyan":
        to_print = term.cyan(text)

    elif color == "green":
        to_print = term.green(text)

    elif color == "magenta":
        to_print = term.magenta(text)

    elif color == "red":
        to_print = term.red(text)

    else:
        to_print = term.white(text)

    if bold:
        print(term.bold(to_print))

    else:
        print(to_print)
