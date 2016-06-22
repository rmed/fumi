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

"""Launcher for fumi."""

__version__ = "0.3.0"

import argparse
import os
import six
import sys

from fumi import util
from fumi.deployer import build_deployer


FUMI_YML = os.path.join(os.getcwd(), 'fumi.yml')


def deploy(conf_name):
    """Deploy using given configuration.

    Arguments:
        conf_name (str): Name of the configuration to use in the deployment.
    """
    status, content = util.read_yaml(FUMI_YML)

    if not status:
        sys.exit(-1)

    if not content:
        util.cprint('There is no fumi.yml file', 'red')
        sys.exit(-1)

    if not conf_name:
        # Find default configuration
        default = None

        for k in content.keys():
            if content[k].get('default'):
                # Found default configuration
                default = k
                util.cprint('Using default configuration: %s' % default)
                break

        if not default:
            # Default not found
            if len(content.keys()) == 0:
                util.cprint('There are no configurations available', 'red')
                sys.exit(-1)

            # Ask for default
            util.cprint('I found the following configurations:')

            for k in content.keys():
                util.cprint('- %s' % k)

            default = six.input("Which one do you want to set as default?: ")

            if default in content.keys():
                content[default]['default'] = True
                util.write_yaml(FUMI_YML, content)

            else:
                # Welp...
                util.cprint('That configuration does not exist!', 'red')
                sys.exit(-1)

        conf_name = default

    elif conf_name not in content.keys():
        util.cprint('Configuration "%s" does not exist' % conf_name, 'red')
        sys.exit(-1)

    # Build deployer
    status, deployer = build_deployer(content[conf_name])

    if not status:
        sys.exit(-1)

    # Deploy!
    result = deployer.deploy()

    if not result:
        sys.exit(-1)


def list_configs():
    """List the configurations present in the fumi.yml file."""
    status, content = util.read_yaml(FUMI_YML)

    if not status:
        sys.exit(-1)

    if not content:
        util.cprint('There is no fumi.yml file', 'red')
        sys.exit(-1)

    for conf in content.keys():
        is_default = content[conf].get('default', False)

        if is_default:
            util.cprint('- %s (default)' % conf)

        else:
            util.cprint('- %s' % conf)


def new_config(name):
    """ Create new basic configuration in fumi.yml file. """
    status, content = util.read_yaml(FUMI_YML)

    if not status:
        sys.exit(-1)

    if not content:
        # Starting from scratch
        content = {}

    if name in content.keys():
        # Do not overwrite configuration
        util.cprint('Configuration "%s" already exists' % name, 'red')
        sys.exit(-1)

    content[name] = {
        'source-type' : '',
        'source-path' : '',

        'predep'  : [],
        'postdep' : [],

        'host'         : '',
        'user'         : '',
        'use-password' : False,
        'password'     : '',
        'deploy-path'  : '',
    }

    status = util.write_yaml(FUMI_YML, content)
    if not status:
        sys.exit(-1)

    util.cprint('Created new blank configuration: %s' % name)


def remove_config(name):
    """Remove a configuration from the fumi.yml file.

    Arguments:
        name (str): Name of the configuration to remove.
    """
    status, content = util.read_yaml(FUMI_YML)

    if not status:
        sys.exit(-1)

    if not content:
        util.cprint('There is no fumi.yml file', 'red')
        sys.exit(-1)

    if name not in content.keys():
        util.cprint('Configuration "%s" does not exist' % name, 'red')
        sys.exit(-1)

    # Remove section
    del content[name]

    status = util.write_yaml(FUMI_YML, content)
    if not status:
        sys.exit(-1)

    util.cprint('Removed configuration: "%s"' % name, 'green')


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


def main():
    """Entrypoint for the program."""
    parser = init_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # No argument provided
        parser.print_help()
        return

    parse_action(sys.argv[1], args)
