# -*- coding: utf-8 -*-

"""
This file is part of Radar.

Radar is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Radar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Lesser GNU General Public License for more details.

You should have received a copy of the Lesser GNU General Public License
along with Radar. If not, see <http://www.gnu.org/licenses/>.

Copyright 2015 - 2017 Lucas Liendo.
"""


from functools import reduce
from json import loads as deserialize_json
from os import stat
from os.path import join as join_path, isabs as is_absolute_path
from shlex import split as split_args
from subprocess import Popen, PIPE
from time import time
from future.utils import listitems
from ..misc import Switchable


class CheckError(Exception):
    pass


class CheckGroupError(Exception):
    pass


class CheckStillRunning(Exception):
    pass


class CheckNotRunning(Exception):
    pass


class CheckOutputAlreadyCollected(Exception):
    pass


class Check(Switchable):

    STATUS = {
        'ERROR': -1,
        'OK': 0,
        'WARNING': 1,
        'SEVERE': 2,
        'UNKNOWN': 3,
        'TIMEOUT': 4,
    }

    """
    The Check class represents a Radar check. A check is run on Radar clients
    using the `Popen` call. The result of a check is collected from stdout.

    This class is both used in Radar server and client. On the server side this class
    is directly used to keep track of all defined checks across all clients. On the
    client side this class is used a base class for platform specific instances
    (UnixCheck and WindowsCheck) which execute checks.

    :param id: A unique integer that identifies a check.
    :param name: A string representing the name of the check.
    :param path: A string containing the path to the check to be executed.
    :param args: A string containing the arguments to be passed to the check.
    :param details: A string containing additional details about a check.
    :param enabled: A boolean indicating if the check is enabled.
    :param platform_setup: A `PlatformSetup` object.
    """

    def __init__(self, id=None, name='', path='', args='', details='', enabled=True, platform_setup=None):
        super(Check, self).__init__(id=id, enabled=enabled)

        if not name or not path:
            raise CheckError("Error - Missing name and/or path from check definition.")

        self.name = name
        self.path = path
        self.args = args
        self.details = details
        self.current_status = self.STATUS['UNKNOWN']
        self.previous_status = self.STATUS['UNKNOWN']
        self.data = None
        self._platform_setup = platform_setup
        self._process_handler = None
        self._start_time = None

    def _update_matches(self, check_status):
        """
        Verify if a check status result matches a `Check`.

        :param check_status: A dictionary containing data related to a `Check`
            execution result. We always expect this dictionary to contain at least
            a status value. Details and data are optional.
        :return: A boolean indicating if the check_status result matches a `Check`.
        """

        return self.enabled and (self.id == check_status['id']) and \
            (check_status['status'] in list(self.STATUS.values()))

    def update_status(self, check_status):
        """
        Update the current `Check` status if the check status matches a `Check`.

        :param check_status: A dictionary containing data related to a `Check`
            execution result. We always expect this dictionary to contain ar least
            a status value. Details and data are optional.
        :return: A boolean indicating its check status has been updated.
        """

        updated = False

        try:
            if self._update_matches(check_status):
                self.previous_status = self.current_status
                self.current_status = check_status['status']
                self.details = check_status.get('details', '')
                self.data = check_status.get('data', None)
                updated = True
        except KeyError:
            raise CheckError("Error - Can't update check's status. Missing id and/or status from check reply.")

        return updated

    @staticmethod
    def get_status(status):
        """
        Return a status name given its integer value.

        :param status: An integer between the range [-1, 4].
        :return: A string containing one of the following values: 'ERROR',
            'OK', 'WARNING', 'SEVERE', 'UNKNOWN' or 'TIMEOUT'.
        """

        # Note: The name of this method should be `get_status_name`.

        try:
            return list(Check.STATUS)[list(Check.STATUS.values()).index(status)]
        except ValueError:
            raise CheckError("Error - Invalid status value : '{}'.".format(status))

    def to_dict(self):
        """
        Return the representation of a `Check` as a dictionary.

        :return: A dictionary containing the following keys: id, name, path,
            args, current_status, previous_status, details, data and enabled.
        """

        return super(Check, self).to_dict([
            'id', 'name', 'path', 'args', 'current_status', 'previous_status',
            'details', 'data', 'enabled',
        ])

    def to_check_dict(self):
        """
        Return a dictionary only containing a `Check` path and arguments.

        :return: A dictionary containing the following keys: id, path
            and args (if available).
        """

        # Note: The name of the method is misleading. It says `to_check_dict`
        # and returns a list with a single element. Its should be `path_and_args`
        # and return a dictionary.

        check_dict = super(Check, self).to_dict(['id', 'path'])

        if self.args:
            check_dict.update({'args': self.args})

        return [check_dict]

    def to_check_reply_dict(self):
        """
        Return a dictionary only containing a `Check` status relevant data.

        :return: A dictionary containing the following keys: id, status,
            details (if available) and data (if available).
        """

        # Note: The name of this method should be `current_status`.

        check_reply_dict = {
            'id': self.id,
            'status': self.current_status,
        }

        if self.details:
            check_reply_dict.update({'details': self.details})

        if self.data:
            check_reply_dict.update({'data': self.data})

        return check_reply_dict

    def _deserialize_output(self, output):
        """
        Try to deserialize the JSON output of a `Check`.

        :param output: A JSON string representing the output of a `Check`.
        :return: The deserialized output as a dictionary.
        """

        try:
            valid_fields = ['status', 'details', 'data']
            deserialized_output = {k.lower(): v for k, v in listitems(deserialize_json(output)) if k.lower() in valid_fields}
            deserialized_output.update({
                'status': self.STATUS[deserialized_output['status'].upper()],
                'id': self.id,
            })
        except ValueError as error:
            raise CheckError("Error - Couldn't parse JSON from check output. Details : {}".format(error))
        except KeyError:
            raise CheckError("Error - Missing or invalid 'status' from check output.")

        return deserialized_output

    def _build_absolute_path(self):
        """
        Construct an absolute path to the corresponding check.

        :return: A string containing the path to the check.
        """

        checks_directory = self._platform_setup.PLATFORM_CONFIG['checks']

        return [self.path if is_absolute_path(self.path) else join_path(checks_directory, self.path)]

    def _split_args(self):
        """
        Split the `self.args` string containing the arguments to be passed to the check.

        :return: A list containing all arguments needed by a check.
        """

        return split_args(self.args)

    def _owned_by_stated_user(self, filename):
        """
        Plaform dependent method to verify if the user owns the check filename.

        :return: A boolean indicating if the user owns a filename.
        """

    def _call_popen(self):
        """
        Run the check and return its result read from stdout.

        :return: A string containing the result of the executed check.
        """

        absolute_path = self._build_absolute_path()
        filename = absolute_path[len(absolute_path) - 1]

        if self._platform_setup.config['enforce ownership'] and not self._owned_by_stated_user(filename):
            raise CheckError("Error - '{}' is not owned by user : {} / group : {}.".format(
                filename,
                self._platform_setup.config['run as']['user'],
                self._platform_setup.config['run as']['group']
            ))

        try:
            return Popen(absolute_path + self._split_args(), stdout=PIPE)
        except OSError as error:
            raise CheckError("Error - Couldn't run : {} check. Details : {}.".format(absolute_path, error))

    def run(self):
        """
        Run a check and update its status. If for any reason a check fails
        to run we set its current status to `ERROR` and store the exception details.

        :return: A `Check` object.
        """

        try:
            self._process_handler = self._call_popen()
            self._start_time = time()
        except CheckError as error:
            self.current_status = self.STATUS['ERROR']
            self.details = str(error)

        return self

    def collect_output(self):
        """
        Collect a `Check` output from stdout and update its status.

        :return: A `Check` object.
        """

        if self.has_finished():
            try:
                self.update_status(self._deserialize_output(self._process_handler.communicate()[0]))
            except ValueError:
                raise CheckOutputAlreadyCollected()
            except AttributeError:
                pass
        else:
            raise CheckStillRunning("Error - Can't collect output. Check's still running.")

        return self

    def _terminate(self):
        """
        Plaform dependent method that terminates a check.
        """

    def terminate(self):
        """
        Forcibly terminate a `Check`. If a check is terminated forcibly
        then its status is updated to `TIMEOUT`. Also the details are
        updated to reflect that the current timeout was exceeded.
        """

        try:
            self._terminate()
            self.current_status = self.STATUS['TIMEOUT']
            self.details = "Check '{} {}' was forcibly terminated. Maximum check execution time ({} seconds) exceeded.".format(
                self.path, self.args, self._platform_setup.config['check timeout'])
            self._process_handler = None
        except CheckNotRunning:
            pass

    def has_finished(self):
        """
        Verify if a `Check` has finished.

        :return: A boolean indicating if a `Check` has finished executing.
        """

        return self._process_handler.poll() is not None

    def is_overdue(self):
        """
        Verify if a `Check` has exceeded its maximum execution time.

        :return: A boolean indicating if a `Check` is still running
            after a maximum time limit.
        """

        overdue = False

        if not self.has_finished():
            try:
                overdue = (time() - self._start_time) > self._platform_setup.config['check timeout']
            except TypeError:
                pass

        return overdue

    def __eq__(self, other_check):
        """
        Compare if two checks are the same. Two checks are considered
        equal if their name, path and args are the same.

        :param other_check: A `Check` object.
        :return: A boolean indicating if a `Check` is equal to another one.
        """

        return self.name == other_check.name and self.path == other_check.path and \
            self.args == other_check.args

    def __hash__(self):
        """
        Return the hash of a `Check` object for comparison purposes taking
        into account its name, path and args.

        :return: An integer value representing the hash of a `Check`.
        """

        return hash(self.name) ^ hash(self.path) ^ hash(self.args)


class UnixCheck(Check):

    """
    The UnixCheck class is a subclass of Check with some overriden and
    added methods in order to properly verify, execute and terminate a check
    on Unix platforms.
    """

    def __new__(cls, *args, **kwargs):
        try:
            global getpwnam, kill, SIGKILL
            from pwd import getpwnam
            from os import kill
            from signal import SIGKILL
        except ImportError:
            raise CheckError("Error - Unable to instantiate UnixCheck. Dependent modules unavailable.")

        return super(UnixCheck, cls).__new__(cls, *args, **kwargs)

    def _owned_by_user(self, filename):
        """
        Verify that a filename is owned by the specified user.

        :param: A boolean indicating if the filename is owned by the specified user.
        """

        user = self._platform_setup.config['run as']['user']

        try:
            return getpwnam(user).pw_uid == stat(filename).st_uid
        except KeyError:
            raise CheckError("Error - User : '{}' doesn't exist.".format(user))

    def _owned_by_group(self, filename):
        """
        Verify that a filename is owned by the specified group.

        :param: A boolean indicating if the filename is owned by the specified group.
        """

        group = self._platform_setup.config['run as']['group']

        try:
            return getpwnam(group).pw_gid == stat(filename).st_gid
        except KeyError:
            raise CheckError("Error - Group : '{}' doesn\'t exist.".format(group))

    def _owned_by_stated_user(self, filename):
        """
        Template method that verifies that a filename is owned by
        the specified user and group.

        :param: A boolean indicating if the filename is owned by the
            specified user and group.
        """

        try:
            return self._owned_by_user(filename) and self._owned_by_group(filename)
        except OSError:
            raise CheckError("Error - Filename : {} does not exist.".format(filename))

    def _terminate(self):
        """
        Terminate a `Check`.

        We achieve this by sending the SIGKILL signal to the spawned process.
        """

        if not self.has_finished():
            try:
                kill(self._process_handler.pid, SIGKILL)
            except (OSError, AttributeError):
                raise CheckNotRunning()


class WindowsCheck(Check):

    """
    The WindowsCheck class is a subclass of Check with some overriden and
    added methods in order to properly verify, execute and terminate a check
    on Windows platforms.
    """

    def __new__(cls, *args, **kwargs):
        try:
            global FindExecutable, FindExecutableError, GetFileSecurity, LookupAccountSid, OWNER_SECURITY_INFORMATION
            global OpenProcess, TerminateProcess, CloseHandle, Win32Error
            global PROCESS_TERMINATE
            from win32security import GetFileSecurity, LookupAccountSid, OWNER_SECURITY_INFORMATION
            from win32api import FindExecutable, OpenProcess, TerminateProcess, CloseHandle
            from pywintypes import error as Win32Error
            from win32con import PROCESS_TERMINATE
        except ImportError:
            raise CheckError("Error - Unable to instantiate WindowsCheck. Dependent modules unavailable.")

        return super(WindowsCheck, cls).__new__(cls, *args, **kwargs)

    def _find_interpreter(self, filename):
        """
        Lookup the executable that interprets a given filename.

        If the file isn't just executable we need to know who interprets this filetype,
        otherwise Popen fails on Windows platforms.

        :param filename: A string containing a path to an executable (or not) file.
        :return: A string containing the program which interprets the filename.
        """

        try:
            return FindExecutable(filename)
        except Win32Error as error:
            raise CheckError("Error - Couldn't find executable for : {}. Details : {}.".format(filename, error))

    def _build_absolute_path(self):
        """
        Return a path containing the interpreter of the check and the check path itself.

        :return: A string containing the path to the interpreter and the check to execute.
        """

        absolute_path = super(WindowsCheck, self)._build_absolute_path().pop()
        _, interpreter = self._find_interpreter(absolute_path)
        executable = [interpreter, absolute_path]

        if interpreter == absolute_path:
            executable.pop()

        return executable

    def _owned_by_user(self, filename):
        """
        Verify that a filename is owned by the specified user.

        :param: A boolean indicating if the filename is owned by the specified user.
        """

        try:
            security_descriptor = GetFileSecurity(filename, OWNER_SECURITY_INFORMATION)
            user, _, _ = LookupAccountSid(None, security_descriptor.GetSecurityDescriptorOwner())
            return user == self._platform_setup.config['run as']['user']
        except MemoryError as error:
            raise CheckError("Error - Couldn't get owner of : {}. Details : {}.".format(filename, error))

    def _owned_by_stated_user(self, filename):
        """
        Template method that verifies that a filename is owned by the specified user.

        :param: A boolean indicating if the filename is owned by the specified user.
        """
        return self._owned_by_user(filename)

    def _split_args(self):
        """
        Split the string containing the arguments to be passed to the check.
        On Windows platforms we need to set the posix kwarg to `False`
        in order to have properly split arguments.

        :return: A list containing all arguments needed by a check.
        """

        return split_args(self.args, posix=False)

    def _terminate(self):
        """
        Terminate a `Check`. We call `TerminateProcess` from win32api.
        """

        if not self.has_finished():
            try:
                handle = OpenProcess(PROCESS_TERMINATE, False, self._process_handler.pid)
                TerminateProcess(handle, -1)
                CloseHandle(handle)
            except Win32Error:
                raise CheckNotRunning()


class CheckGroup(Switchable):

    """
    The CheckGroup class contains a collection of checks.

    :param name: A string containing the name of the `CheckGroup`.
    :param checks: A list containing `Check` objects.
    :param enabled: A boolean indicating if the `CheckGroup` is enabled.
    """

    def __init__(self, name='', checks=None, enabled=True):
        super(CheckGroup, self).__init__(enabled=enabled)

        if not name or not checks:
            raise CheckGroupError("Error - Missing name and/or checks from check group definition.")

        self.name = name
        self.checks = set(checks) if checks is not None else []

    def update_status(self, check_status):
        """
        Try to update a `Check` status.

        :return: A boolean indicating if any of the checks of a `CheckGroup`
            has been updated.
        """

        return any([check.update_status(check_status) for check in self.checks])

    def to_dict(self):
        """
        Return the representation of a `CheckGroup` as a dictionary.

        :return: A dictionary containing the following keys: id, name, enabled,
            and checks.
        """

        check_group_dict = super(CheckGroup, self).to_dict(['id', 'name', 'enabled'])
        check_group_dict.update({'checks': [check.to_dict() for check in self.checks]})

        return check_group_dict

    def to_check_dict(self):
        return reduce(lambda l, m: l + m, [check.to_check_dict() for check in self.checks])

    def as_list(self):
        """
        Construct a list containing all `Checks` defined within this `CheckGroup`.

        :return: A list containing all checks defined in a `CheckGroup`.
        """

        return [check for check in self.checks]

    def __eq__(self, other_check_group):
        """
        Compare if two check groups are the same. Two check groups are considered
        equal if their name and their respective checks are the same.

        :param other_check_groupd: A `CheckGroup` object.
        :return: A boolean indicating if a `CheckGroup` is equal to another one.
        """

        return self.name == other_check_group.name and self.checks == other_check_group.checks

    def __hash__(self):
        """
        Return the hash of a `CheckGroup` object for comparison purposes taking
        into account its name and the hashes of its checks.

        :return: An integer value representing the hash of a `CheckGroup`.
        """

        if len(self.checks) > 1:
            hashed = hash(self.name) ^ reduce(lambda l, m: l.__hash__() ^ m.__hash__(), self.checks)
        else:
            hashed = hash(self.name) ^ list(self.checks).pop().__hash__()

        return hashed

    def enable(self, ids):
        """
        Enable one or more checks.

        :param ids: A list containing the ids to be enabled. The list can
            include `Check` and `CheckGroup` ids.
        :return: A list containing ids of `Check` and `CheckGroup`
            objects that were enabled.
        """

        return ([self.id] if super(CheckGroup, self).enable(ids=ids) else []) + \
            [check.id for check in self.checks if check.enable(ids=ids)]

    def disable(self, ids):
        """
        Disable one or more checks.

        :param ids: A list containing check ids to be disabled. The list can
            include `Check` and `CheckGroup` ids.
        :return: A list containing ids of `Check` and `CheckGroup`
            objects that were disabled.
        """

        return ([self.id] if super(CheckGroup, self).disable(ids=ids) else []) + \
            [check.id for check in self.checks if check.disable(ids=ids)]
