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
import datetime
import os
import paramiko
import scp
import subprocess
import sys
import tarfile

def deploy_local(deployment):
    """ Local based deployment. """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(deployment.host, username=deployment.user)

    # Run pre-deployment commands
    if deployment.pre_local:
        for cmd in deployment.pre_local:
            print("Running local command:", cmd)
            subprocess.Popen(cmd, shell=True).wait()

    # Usually executed relative to user directory (~/)
    if deployment.pre_remote:
        for cmd in deployment.pre_local:
            print("Running remote command:", cmd)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # TODO: better handling for SSH return codes?
            # print(stdout.channel.recv_exit_status())
            print(*stdout.readlines())

    # Compress source to temporary directory
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    comp_file = timestamp + ".tar.gz"
    tmp_local = os.path.join("/tmp", comp_file)
    print("Compressing source to /tmp/%s" % comp_file)

    with tarfile.open(tmp_local, "w:gz") as tar:
        tar.add(deployment.s_path, arcname=timestamp)

    # Upload compressed source
    print("Uploading %s..." % comp_file)

    uload = scp.SCPClient(ssh.get_transport())
    uload_tmp = deployment.h_tmp or "/tmp"
    uload_path = os.path.join(uload_tmp, comp_file)

    try:
        uload.put(tmp_local, uload_path)

    except scp.SCPException as e:
        sys.exit("Error uploading to server", e)

    # Uncompress source to deploy_path/rev
    print("Uncompressing remote file...")

    rev_path = os.path.join(deployment.d_path, "rev")
    untar = "tar -C %s -zxvf %s" % (rev_path, uload_path)

    stdin, stdout, stderr = ssh.exec_command(untar)
    status = stdout.channel.recv_exit_status()

    if status == 147:
        sys.exit("Error: tar command not found in remote host")
    elif status == 1:
        print(*stderr.readlines())
        sys.exit("Error: some files differ")
    elif status == 2:
        print(*stderr.readlines())
        sys.exit("Fatal error when extracting remote file")

    # Link directory
    print("Linking directory")

    link_path = os.path.join(deployment.d_path, "current")
    current_rev = os.path.join(rev_path, timestamp)
    ln = "ln -sfn %s %s" % (current_rev, link_path)

    stdin, stdout, stderr = ssh.exec_command(ln)
    # status = stdout.channel.recv_exit_status()

    # Run post-deployment commands
    if deployment.post_local:
        for cmd in deployment.pre_local:
            print("Running local command:", cmd)
            subprocess.Popen(cmd, shell=True).wait()

    # Executed relative to deploy_path/current
    if deployment.post_remote:
        for cmd in deployment.pre_local:
            print("Running remote command:", cmd)
            cd_command = "cd %s; %s" % (link_path, cmd)
            stdin, stdout, stderr = ssh.exec_command(cd_command)
            # TODO: better handling for SSH return codes?
            # print(stdout.channel.recv_exit_status())
            print(*stdout.readlines())

    # Clean revisions
    if deployment.keep:
        print("Checking for old revisions...")

        stdin, stdout, stderr = ssh.exec_command("ls %s" % rev_path)
        status = stdout.channel.recv_exit_status()

        if status == 1 or status == 2:
            print(*stderr.readlines())
            sys.exit("Error obtaining list of revisions")

        revisions = stdout.readlines()

        if len(revisions) > deployment.keep:
            old_revisions = []

            while len(revisions) > deployment.keep:
                old_revisions.append(revisions.pop(0))

            for r in old_revisions:
                print("Removing revision", r.strip())
                rm_old = "rm -rf %s" % os.path.join(rev_path, r.strip())
                stdin, stdout, stderr = ssh.exec_command(rm_old)

    # Cleanup temporary files
    print("Cleaning temporary files...")

    subprocess.call(["rm", tmp_local])
    stdin, stdout, stderr = ssh.exec_command("rm %s" % uload_path)

    print("Deployment complete!")

def deploy_git(deployment):
    """ Git based deployment. """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(deployment.host, username=deployment.user)

    # Run pre-deployment commands
    if deployment.pre_local:
        for cmd in deployment.pre_local:
            print("Running local command:", cmd)
            subprocess.Popen(cmd, shell=True).wait()

    # Usually executed relative to user directory (~/)
    if deployment.pre_remote:
        for cmd in deployment.pre_local:
            print("Running remote command:", cmd)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            # TODO: better handling for SSH return codes?
            # print(stdout.channel.recv_exit_status())
            print(*stdout.readlines())

    # Checkout source
    print("Cloning repository...")

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    rev_path = os.path.join(deployment.d_path, "rev")
    current_rev = os.path.join(deployment.d_path, "rev", timestamp)
    clone = "git clone %s %s" % (deployment.s_path, current_rev)

    stdin, stdout, stderr = ssh.exec_command(clone)
    status = stdout.channel.recv_exit_status()

    if status == 147:
        sys.exit("git command not found in remote server")
    # TODO: check git exit codes

    # Link directory
    print("Linking directory")

    link_path = os.path.join(deployment.d_path, "current")
    ln = "ln -sfn %s %s" % (current_rev, link_path)

    stdin, stdout, stderr = ssh.exec_command(ln)
    # status = stdout.channel.recv_exit_status()

    # Run post-deployment commands
    if deployment.post_local:
        for cmd in deployment.pre_local:
            print("Running local command:", cmd)
            subprocess.Popen(cmd, shell=True).wait()

    # Executed relative to deploy_path/current
    if deployment.post_remote:
        for cmd in deployment.pre_local:
            print("Running remote command:", cmd)
            cd_command = "cd %s; %s" % (link_path, cmd)
            stdin, stdout, stderr = ssh.exec_command(cd_command)
            # TODO: better handling for SSH return codes?
            # print(stdout.channel.recv_exit_status())
            print(*stdout.readlines())

    # Clean revisions
    if deployment.keep:
        print("Checking for old revisions...")

        stdin, stdout, stderr = ssh.exec_command("ls %s" % rev_path)
        status = stdout.channel.recv_exit_status()

        if status == 1 or status == 2:
            print(*stderr.readlines())
            sys.exit("Error obtaining list of revisions")

        revisions = stdout.readlines()

        if len(revisions) > deployment.keep:
            old_revisions = []

            while len(revisions) > deployment.keep:
                old_revisions.append(revisions.pop(0))

            for r in old_revisions:
                print("Removing revision", r.strip())
                rm_old = "rm -rf %s" % os.path.join(rev_path, r.strip())
                stdin, stdout, stderr = ssh.exec_command(rm_old)

    print("Deployment complete!")
