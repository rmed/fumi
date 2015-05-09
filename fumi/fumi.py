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
from fumi.deployments import *
# from deployments import * # For development
import argparse
import os
import sys
import yaml
if sys.version[0] == "3": raw_input=input

__version__ = "0.2.0"

CWD = os.getcwd()
DEP_CONF = os.path.join(CWD, 'fumi.yml')


class Deployment(object):
    """ Configuration parsed from the fumi.yml file """

    def __init__(self, **kwargs):
        # Source information
        self.s_type = kwargs['source-type']
        self.s_path = kwargs['source-path']

        # Pre-deployment commands
        self.predep = None
        predep = kwargs.get('predep')

        if predep:
            self.predep = predep

        # Post-deployment commands
        self.postdep = None
        postdep = kwargs.get('postdep')

        if postdep:
            self.postdep = postdep

        # Destination host information
        self.host = kwargs['host']
        self.user = kwargs['user']
        self.d_path = kwargs['deploy-path']

        # Optional information
        self.h_tmp = kwargs.get('host-tmp')
        self.keep = kwargs.get('keep-max')
        self.default = kwargs.get('default')
        self.local_ign = kwargs.get('local-ignore')


def deploy(configuration):
    """ Deploy with given configuration. """
    content = read_yaml()
    if not content:
        sys.exit("There is no fumi.yml file")

    if not configuration:
        default = None

        for k in content.keys():
            if content[k].get("default"):
                default = k
                print("Using default configuration '%s'" % default)
                break

        if not default:
            if len(content.keys()) == 0:
                sys.exit("There are no configurations")

            # Ask for default
            print("I found the following configurations:")

            for k in content.keys():
                print("-", k)

            default = raw_input("Which one do you want to set as default?: ")

            if default in content.keys():
                content[default]["default"] = True
                write_yaml(content)

            else:
                sys.exit("That configuration does not exist!")

        configuration = default

    elif configuration not in content.keys():
        sys.exit("Configuration '%s' does not exist" % configuration)

    # Build deployment object
    dep = Deployment(**content[configuration])

    if dep.s_type == "local":
        deploy_local(dep)

    elif dep.s_type == "git":
        deploy_git(dep)

def list_configs():
    """ List the configurations present in the fumi.yml file. """
    content = read_yaml()
    if not content:
        sys.exit("There is no fumi.yml file")

    for conf in content.keys():
        print(conf)

def new_config(name):
    """ Create new basic configuration in fumi.yml file. """
    content = read_yaml()
    if not content:
        content = {}

    if name in content.keys():
        sys.exit("Configuration '%s' already exists" % name)

    content[name] = {
        "source-type": "",
        "source-path": "",

        "predep": {
            "local": None,
            "remote": None
        },
        "postdep": {
            "local": None,
            "remote": None
        },

        "host": "",
        "user": "",
        "deploy-path": "",
    }

    write_yaml(content)

    print("Created new blank configuration '%s'" % name)

def remove_config(name):
    """ Remove a configuration from the fumi.yml file. """
    content = read_yaml()
    if not content:
        sys.exit("There is no fumi.yml file")

    if name not in content.keys():
        sys.exit("Configuration %s does not exist" % name)

    del content[name]

    write_yaml(content)

    print("Removed configuration '%s'" % name)

def read_yaml():
    """ Reads the fumi.yml file and returns the parsed information
        in a dict() object.

        If there is no file, then returns None
    """
    if os.path.isfile(DEP_CONF):
        with open(DEP_CONF, 'r') as fumi_yml:
            try:
                content = yaml.load(fumi_yml)

            except (yaml.YAMLError, e):
                sys.exit("Error in deployment file:", e)

        return content

    return None

def write_yaml(content):
    """ Overwrites the content of the fumi.yml file. """
    with open(DEP_CONF, 'w') as fumi_yml:
        try:
            yaml.dump(content, fumi_yml, default_flow_style=False)

        except (yaml.YAMLError, e):
            sys.exit("Error writing yaml to deployment file:", e)

def init_parser():
    """ Initialize the arguments parser. """
    parser = argparse.ArgumentParser(
        description="Simple deployment tool")

    parser.add_argument('--version', action='version',
        version='%(prog)s ' + __version__)

    subparsers = parser.add_subparsers(title="commands")

    # deploy
    parser_deploy = subparsers.add_parser("deploy",
        help="deploy with given configuration")
    parser_deploy.add_argument("configuration", nargs="?",
        help="configuration to use")

    # list
    parser_list = subparsers.add_parser("list",
        help="list all the available deployment configurations")

    # new
    parser_new = subparsers.add_parser("new",
        help="create new deployment configuration")
    parser_new.add_argument("name", help="name for the configuration")

    # remove
    parser_remove = subparsers.add_parser("remove",
        help="remove a configuration from the deployment file")
    parser_remove.add_argument("name", help="name of the configuration")

    return parser

def parse_action(action, parsed):
    """ Parse the action to execute. """
    if action == 'deploy':
        deploy(parsed.configuration)

    elif action == 'list':
        list_configs()

    elif action == 'new':
        new_config(parsed.name)

    elif action == 'remove':
        remove_config(parsed.name)

    else:
        parser.print_help()


def main():
    parser = init_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # No argument provided
        parser.print_help()
        return

    parse_action(sys.argv[1], args)

# Only for development
# if __name__ == "__main__":
    # main()
