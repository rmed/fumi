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

"""Message strings."""

import gettext

CMD_EXEC = _('Command execution')
CMD_LOCAL = _('Running local command: %s')
CMD_REMOTE = _('Running remote command: %s')
CMD_SKIP = _('Skipping unknown command type "%s"')

# NOTE: The named configuration already exists in the file
CONF_EXISTS = _('Configuration "%s" already exists')
# NOTE: The chosen configuration does not exist
CONF_NAME_NOT_FOUND = _('Configuration "%s" does not exist')
CONF_NOT_FOUND = _('That configuration does not exist!')
# NOTE: Name of configuration that was removed
CONF_REMOVED = _('Removed configuration: %s')
# NOTE: Shows list of configuration names to user
CONF_SET_DEF = _('Which one do you want to set as default?: ')
# NOTE: List of configurations after scanning the YML file
CONFS_FOUND = _('I found the following configurations:')

CONN_AUTH_FAIL = _('Authentication failed')
CONN_FAIL = _('Could not connect, please check your credentials')
CONN_NEEDPASS = _('Connection needs a password')
CONN_KEYPASS = _('Password needed to unlock private key file')
# NOTE: When introducing password manually
CONN_PASS = _('Password: ')
CONN_PUBKEY = _('Trying to connect using public key')
CONN_TRYPASS = _('Trying to connect using provided password')

CORRECT = _('Correct!')

# NOTE: Created empty configuration template, shows name
CREATED_BLANK = _('Created blank configuration: %s')

DEP_COMPLETE = _('Deployment complete!')
DEP_CHECK_REMOTE = _('Checking remote directories...')
DEP_CONNECTED = _('Connected!')
DEP_CONNECTING = _('Connecting to %s as %s...')
DEP_CREATEDIR = _('Creating remote directory tree...')
DEP_GIT = _('Performing a "git" deployment')
DEP_GIT_CLONE = _('Cloning repository...')
DEP_GIT_NOTFOUND = _('git command not found in remote server')
DEP_LOCAL = _('Performing a "local"deployment')
DEP_LOCAL_CLEAN = _('Cleaning temporary files...')
DEP_LOCAL_COMPRESS = _('Compressing source to %s')
DEP_LOCAL_ERR1 = _('Error: some files differ')
DEP_LOCAL_ERR127 = _('Error: tar command not found in remote host')
DEP_LOCAL_ERR2 = _('Fatal error when extracting remote file')
DEP_LOCAL_PATHNOEXIST = _('Path "%s" does not exist, ignoring')
DEP_LOCAL_SCPFAIL = _('Failed to initiate SCP, check configuration')
DEP_LOCAL_UNCOMPRESS = _('Uncompressing remote file...')
DEP_LOCAL_UPLOAD = _('Uploading %s...')
DEP_LOCAL_UPLOADERR = _('Error uploading to server: %s')
DEP_MISSING_PARAM = _('Missing required parameter: %s')
DEP_PREPARE_COMPLETE = _('Preparation complete!')
DEP_PREPARE_REV = _('Preparing revision %s')
DEP_PREPARE_NOTICE = _('Make sure to upload shared files before deploying')
DEP_UNKNOWN = _('Unknown deployment type: %s')

DONE = _('Done!')

# NOTE: Command line title for the commands section
FUMI_CMDS = _('commands')
FUMI_CONF = _('configuration')
FUMI_CONF_DESC = _('configuration to use')
FUMI_DEPLOY_DESC = _('deploy using given configuration')
FUMI_DESC = _('Simple deployment tool')
FUMI_LIST_DESC = _('list all the available deployment configurations')
FUMI_NAME = _('name')
FUMI_NAME_DESC = _('name for the new configuration')
FUMI_NEW_DESC = _('create new deployment configuration')
FUMI_PREP_DESC = _('test connection and prepare remote directories')
FUMI_RM_DESC = _('remove a configuration from the deployment file')
# TODO: Shown when trying to execute an unknown action
FUMI_UNKNOWN = _('Unknown action')

LINK_DIR = _('Linking directory...')
LINK_SHARED = _('Linking shared files...')
LINKING = _('Linking: %s')

# NOTE: When listing configurations, the default one is marked as such
LIST_DEFAULT = _('- %s (default)')
NO_CONFS = _('There are no configurations available')
NO_YML = _('There is no fumi.yml file')

PATH_NOEXIST = _('Path "%s" does not exist')

REMOTE_DEP_CREATE_ERR = _('Cannot create remote deployment directory')
REMOTE_DEP_NOEXIST = _('Remote deployment directory does not exist')
REMOTE_FILE_NOEXIST = _('Remote file "%s" does not exist')
REMOTE_REV_CREATE_ERR = _('Cannot create remote revisions directory')
REMOTE_REV_NOEXIST = _('Remote revisions directory does not exist')
REMOTE_SHR_CREATE_ERR = _('Cannot create remote shared directory')
REMOTE_SHR_NOEXIST = _('Remote shared directory does not exist')
REMOTE_TMP_CREATE_ERR = _('Cannot create remote temporary directory')
REMOTE_TMP_NOEXIST = _('Remote temporary directory does not exist')

REV_CHECK = _('Checking old revisions...')
REV_LINK_PREV = _('Linking previous revision (%s) ...')
REV_LIST_ERR = _('Error obtaining list of revisions')
REV_PREV_MISSING = _('No previous revision to link')
# NOTE: ID of the revision being removed
REV_RM = _('Removing revision %s')
REV_RM_REMOTE = _('Removing remote revision %s ...')

# NOTE: First token is the path, the second is the exception
RM_ERR = _('Could not remove "%s": %s')
# NOTE: Next lines are directly read from stderr
RM_ERR_REMOTED = _('Remote error, could not remove directory:')
# NOTE: Next lines are directly read from stderr
RM_ERR_REMOTEF = _('Remote error, could not remove file:')
# NOTE: Only shows filename
RM_FAIL = _('Failed to remove file: %s')
# NOTE: Path being removed
RM_MSG_LOCAL = _('Removing %s ...')
RM_MSG_REMOTE = _('Removing remote file %s ...')

ROLLBACK_BEGIN = _('Beginning rollback...')

# TODO: Includes exception message
UNEXPECTED_ERR = _('Unexpected error: %s')

# NOTE: Token represents name of the default configuration
USE_DEFAULT_CONF = _('Using default configuration: %s')

# NOTE: Includes the error message
YML_ERR = _('Error in deployment file: %s')
# NOTE: Includes the error message
YML_WRITE_ERR = _('Error writing yaml to deployment file: %s')
