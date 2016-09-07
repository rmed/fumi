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

"""Launcher for fumi.

This parses the command line arguments and performs the different operations.
"""

__version__ = '0.4.0'

# Set locale
from pkg_resources import resource_filename
import six
import gettext

_locale_dir = resource_filename(__name__, 'locale')
if six.PY3:
    gettext.install('fumi', _locale_dir)
else:
    gettext.install('fumi', _locale_dir, unicode=True)


import argparse
import os
import sys

from fumi import messages as m
from fumi import util
from fumi.deployer import build_deployer


FUMI_YML = os.path.join(os.getcwd(), 'fumi.yml')


def deploy(conf_name, prepare=False):
    """Deploy using given configuration.

    Arguments:
        conf_name (str): Name of the configuration to use in the deployment.
        prepare (bool): Whether or not this is a preparation deployment.
            A preparation simply checks connection and creates the remote
            directory tree.
    """
    status, content = util.read_yaml(FUMI_YML)

    if not status:
        sys.exit(-1)

    if not content:
        util.cprint(m.NO_YML, 'red')
        sys.exit(-1)

    if not conf_name:
        # Find default configuration
        default = None

        for k in content.keys():
            if content[k].get('default'):
                # Found default configuration
                default = k
                util.cprint(m.USE_DEFAULT_CONF % default)
                break

        if not default:
            # Default not found
            if len(content.keys()) == 0:
                util.cprint(m.NO_CONFS, 'red')
                sys.exit(-1)

            # Ask for default
            util.cprint(m.CONFS_FOUND)

            for k in content.keys():
                util.cprint('- %s' % k)

            default = six.moves.input(m.CONF_SET_DEF)

            if default in content.keys():
                content[default]['default'] = True
                util.write_yaml(FUMI_YML, content)

            else:
                # Welp...
                util.cprint(m.CONF_NOT_FOUND, 'red')
                sys.exit(-1)

        conf_name = default

    elif conf_name not in content.keys():
        util.cprint(m.CONF_NAME_NOT_FOUND % conf_name, 'red')
        sys.exit(-1)

    # Build deployer
    status, deployer = build_deployer(content[conf_name])

    if not status:
        sys.exit(-1)

    if prepare:
        # Preparation
        result = deployer.prepare()

    else:
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
        util.cprint(m.NO_YML, 'red')
        sys.exit(-1)

    for conf in content.keys():
        is_default = content[conf].get('default', False)

        if is_default:
            util.cprint(m.LIST_DEFAULT % conf)

        else:
            util.cprint('- %s' % conf)


def new_config(name):
    """Create new basic configuration in fumi.yml file.

    Arguments:
        name (str): Name for the new configuration.
    """
    status, content = util.read_yaml(FUMI_YML)

    if not status:
        sys.exit(-1)

    if not content:
        # Starting from scratch
        content = {}

    if name in content.keys():
        # Do not overwrite configuration
        util.cprint(m.CONF_EXISTS % name, 'red')
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

    util.cprint(m.CREATED_BLANK % name)


def remove_config(name):
    """Remove a configuration from the fumi.yml file.

    Arguments:
        name (str): Name of the configuration to remove.
    """
    status, content = util.read_yaml(FUMI_YML)

    if not status:
        sys.exit(-1)

    if not content:
        util.cprint(m.NO_YML, 'red')
        sys.exit(-1)

    if name not in content.keys():
        util.cprint(m.CONF_NAME_NOT_FOUND % name, 'red')
        sys.exit(-1)

    # Remove section
    del content[name]

    status = util.write_yaml(FUMI_YML, content)
    if not status:
        sys.exit(-1)

    util.cprint(m.CONF_REMOVED % name, 'green')


def init_parser():
    """ Initialize the arguments parser. """
    parser = argparse.ArgumentParser(description=m.FUMI_DESC)

    parser.add_argument('--version', action='version',
        version='%(prog)s ' + __version__)

    subparsers = parser.add_subparsers(title=m.FUMI_CMDS)


    # deploy
    parser_deploy = subparsers.add_parser('deploy', help=m.FUMI_DEPLOY_DESC)
    parser_deploy.add_argument(
        'configuration',
        nargs='?',
        metavar=m.FUMI_CONF,
        help=m.FUMI_CONF_DESC
    )


    # list
    parser_list = subparsers.add_parser('list', help=m.FUMI_LIST_DESC)


    # new
    parser_new = subparsers.add_parser('new', help=m.FUMI_NEW_DESC)
    parser_new.add_argument(
        'name',
        metavar=m.FUMI_NAME,
        help=m.FUMI_NAME_DESC
    )


    # prepare
    parser_prepare = subparsers.add_parser('prepare', help=m.FUMI_PREP_DESC)
    parser_prepare.add_argument(
        'configuration',
        nargs='?',
        metavar=m.FUMI_CONF,
        help=m.FUMI_CONF_DESC
    )


    # remove
    parser_remove = subparsers.add_parser('remove', help=m.FUMI_RM_DESC)
    parser_remove.add_argument(
        'name',
        metavar=m.FUMI_NAME,
        help=m.FUMI_NAME_DESC
    )

    return parser

def parse_action(action, parsed):
    """ Parse the action to execute. """
    if action == 'deploy':
        deploy(parsed.configuration)

    elif action == 'list':
        list_configs()

    elif action == 'new':
        new_config(parsed.name)

    elif action == 'prepare':
        deploy(parsed.configuration, prepare=True)

    elif action == 'remove':
        remove_config(parsed.name)

    else:
        util.cprint(m.FUMI_UNKNOWN)

def main():
    """Entrypoint for the program."""
    parser = init_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # No argument provided
        parser.print_help()
        return

    parse_action(sys.argv[1], args)
