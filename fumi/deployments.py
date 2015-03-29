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
import os
import paramiko
import scp
import subprocess
import sys
import tarfile


term = Terminal()
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def deploy_local(deployment):
    """ Local based deployment. """
    ssh.connect(deployment.host, username=deployment.user)

    _predep(deployment.pre_local, deployment.pre_remote)


    # Compress source to temporary directory
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    comp_file = timestamp + ".tar.gz"
    tmp_local = os.path.join("/tmp", comp_file)

    print(term.bold_cyan("\n# Compressing source to /tmp/%s\n" % comp_file))

    with tarfile.open(tmp_local, "w:gz") as tar:
        tar.add(deployment.s_path, arcname=timestamp)

    print(term.bold_green("Done!"))


    # Upload compressed source
    print(term.bold_cyan("\n# Uploading %s...\n" % comp_file))

    uload = scp.SCPClient(ssh.get_transport())
    uload_tmp = deployment.h_tmp or "/tmp"
    uload_path = os.path.join(uload_tmp, comp_file)

    try:
        uload.put(tmp_local, uload_path)

    except scp.SCPException as e:
        sys.exit(term.bold_red("Error uploading to server: %s" % e))

    print(term.bold_green("Done!"))


    # Uncompress source to deploy_path/rev
    print(term.bold_cyan("\n# Uncompressing remote file...\n"))

    rev_path = os.path.join(deployment.d_path, "rev")
    untar = "tar -C %s -zxvf %s" % (rev_path, uload_path)

    stdin, stdout, stderr = ssh.exec_command(untar)
    status = stdout.channel.recv_exit_status()

    if status == 127:
        sys.exit(term.bold_red("Error: tar command not found in remote host"))
    elif status == 1:
        print(*stderr.readlines())
        sys.exit(term.bold_red("Error: some files differ"))
    elif status == 2:
        print(*stderr.readlines())
        sys.exit(term.bold_red("Fatal error when extracting remote file"))

    print(term.bold_green("Done!"))


    # Link directory
    _symlink(deployment.d_path, rev_path, timestamp)


    # Run post-deployment commands
    _postdep(deployment.post_local, deployment.post_remote,
        os.path.join(deployment.d_path, "current"))


    # Clean revisions
    if deployment.keep:
        _clean_revisions(deployment.keep, rev_path)


    # Cleanup temporary files
    print(term.bold_cyan("\n# Cleaning temporary files...\n"))

    subprocess.call(["rm", tmp_local])
    stdin, stdout, stderr = ssh.exec_command("rm %s" % uload_path)

    print(term.bold_green("Done!"))


    print(term.bold_green("\nDeployment complete!"))

def deploy_git(deployment):
    """ Git based deployment. """
    ssh.connect(deployment.host, username=deployment.user)

    # Run pre-deployment commands
    _predep(deployment.pre_local, deployment.pre_remote)


    # Clone source
    print(term.bold_cyan("\n# Cloning repository...\n"))

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rev_path = os.path.join(deployment.d_path, "rev")
    current_rev = os.path.join(deployment.d_path, "rev", timestamp)
    clone = "git clone %s %s" % (deployment.s_path, current_rev)

    stdin, stdout, stderr = ssh.exec_command(clone)
    status = stdout.channel.recv_exit_status()

    if status == 127:
        sys.exit(term.bold_red("git command not found in remote server"))
    # TODO: check git exit codes

    print(term.bold_green("Done!"))


    # Link directory
    _symlink(deployment.d_path, rev_path, timestamp)


    # Run post-deployment commands
    _postdep(deployment.post_local, deployment.post_remote,
        os.path.join(deployment.d_path, "current"))


    # Clean revisions
    if deployment.keep:
        _clean_revisions(deployment.keep, rev_path)


    print(term.bold_green("\nDeployment complete!"))


def _clean_revisions(keep, rev_path):
    """ Remove old revisions from the remote server.

        Only the most recent revisions will be kept, to a maximum defined
        by the keep argument.
    """
    print(term.bold_cyan("\n# Checking old revisions...\n"))

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
            print(term.bold_magenta("Removing revision %s" % r.strip()))
            rm_old = "rm -rf %s" % os.path.join(rev_path, r.strip())
            stdin, stdout, stderr = ssh.exec_command(rm_old)

    print(term.bold_green("\nDone!"))

def _postdep(local, remote, link_path):
    """ Execute post-deployment commands (both local and remote).

        Note that remote post-deployment commands are executed in the
        directory of the revision that has been deployed
        (deploy_path/current).
    """
    if local:
        for cmd in local:
            print(term.bold_cyan("\n# Running local command: %s\n" % cmd))
            subprocess.Popen(cmd, shell=True).wait()

    # Executed relative to deploy_path/current
    if remote:
        for cmd in remote:
            print(term.bold_cyan("\n# Running remote command: %s\n" % cmd))
            cd_command = "cd %s; %s" % (link_path, cmd)
            stdin, stdout, stderr = ssh.exec_command(cd_command)
            # TODO: better handling for SSH return codes?
            # print(stdout.channel.recv_exit_status())
            print(*stdout.readlines())

def _predep(local, remote):
    """ Execute pre-deployment commands (both local and remote).

        Note that remote pre-deployment commands are usually executed
        in the users directory (~/) when possible.
    """
    if local:
        for cmd in local:
            print(term.bold_cyan("\n# Running local command: %s\n" % cmd))
            subprocess.Popen(cmd, shell=True).wait()

    # Executed relative to user directory
    if remote:
        for cmd in remote:
            print(term.bold_cyan("\n# Running remote command: %s\n" % cmd))
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # TODO: better handling for SSH return codes?
            # print(stdout.channel.recv_exit_status())
            print(*stdout.readlines())

def _symlink(d_path, rev_path, timestamp):
    """ Symlink the deployed revision to the deploy_path/current
        directory.
    """
    print(term.bold_cyan("\n# Linking directory...\n"))

    link_path = os.path.join(d_path, "current")
    current_rev = os.path.join(rev_path, timestamp)
    ln = "ln -sfn %s %s" % (current_rev, link_path)

    stdin, stdout, stderr = ssh.exec_command(ln)
    # status = stdout.channel.recv_exit_status()

    print(term.bold_green("Done!"))
