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


from threading import Thread, Event
from queue import Empty as EmptyQueue
from ..logger import RadarLogger
from ..check import UnixCheck, WindowsCheck, CheckError, CheckStillRunning
from ..protocol import RadarMessage
from ..platform_setup import Platform


class CheckManagerError(Exception):
    pass


class CheckManager(Thread):

    STOP_EVENT_TIMEOUT = 0.2
    AVAILABLE_PLATFORMS = {
        'Unix': UnixCheck,
        'Windows': WindowsCheck,
    }

    """
    The CheckManager is responsible for controlling the execution of checks
    on a Radar client.

    It is also responsible of:
        - Collecting check outputs and get them back to the RadarClient process.
        - Terminating overdue checks.
        - Restrict the total amount of concurrent checks at any time.
        - Terminating all checks if the Radar client is shut down.

    :param platform_setup: A `PlatformSetup` object.
    :param input_queue: A `Queue` object where checks to execute are extracted from.
    :param output_queue: A `Queue` object where check execution outputs are replied to.
    :param stop_event: An `Event` object that is used to control thread
        termination.
    """

    def __init__(self, platform_setup, input_queue, output_queue, stop_event=None):
        Thread.__init__(self)
        self._platform_setup = platform_setup
        self._input_queue = input_queue
        self._output_queue = output_queue
        self.stop_event = stop_event or Event()
        self._check_class = self._get_platform_check_class()
        self._message_actions = {
            RadarMessage.TYPE['CHECK']: self._on_check,
            RadarMessage.TYPE['TEST']: self._on_test,
        }

        # We keep two queues. The self._wait_queue grows without limit and `Check` objects
        # are initially stored in this queue for processing. The self._execution_queue
        # has a fixed size and at any time it holds no more `Check` objects than what the
        # `check concurrency` option specifies.
        self._wait_queue = []
        self._execution_queue = []

    def _validate(self):
        """
        Verify that the `check timeout` and `check concurrency` options hold
        valid values.
        """

        try:
            if float(self._platform_setup['check timeout']) < 1:
                raise CheckManagerError("Error - Check timeout must be at least 1 second.")
        except ValueError:
            raise CheckManagerError("Error - '{}' is not a valid check timeout value.".format(
                self._platform_setup['check timeout']))

        try:
            if int(self._platform_setup['check concurrency']) < 1:
                raise CheckManagerError("Error - Check concurrency value must be at least 1.")
        except ValueError:
            raise CheckManagerError("Error - '{}' is not a valid check concurrency value.".format(
                self._platform_setup['check concurrency']))

    def _get_platform_check_class(self):
        """
        Select the appropriate `Check` platform class that needs to be called
        in order to instantiate platform dependent checks.
        """

        platform = Platform.get_platform_type()

        try:
            return self.AVAILABLE_PLATFORMS[platform]
        except KeyError:
            raise CheckManagerError("Error - Platform : '{}' is not available.".format(platform))

    def _build_checks(self, checks):
        """
        Build a list of `Check` objects from a list of dictionaries containing checks data.

        :param checks: A list of dictionaries containing checks to be created.
        :return: A list containing `Check` objects.
        """

        built_checks = []

        for check in checks:
            try:
                built_checks.append(self._check_class(
                    name=check['path'], platform_setup=self._platform_setup, **check))
            except KeyError:
                RadarLogger.log("Error - Server sent empty or invalid check. Details : {}.".format(check))

        return built_checks

    def _free_slots_amount(self):
        """
        Return an integer indicating the amount of free slots.

        :return: An integer that indicates how many slots are available.
        """

        return self._platform_setup.config['check concurrency'] - len(self._execution_queue)

    def _available_slots(self):
        """
        Return a boolean indicating if there are any available slots.

        :return: A boolean indicating if there is at least one available slot.
        """

        return self._free_slots_amount() > 0

    def _collect_outputs(self):
        """
        Collect any available check data outputs.

        :return: A list of dictionaries containing check data outputs.
        """

        check_outputs = []

        for check in self._execution_queue:
            try:
                check_outputs.append(check.collect_output().to_check_reply_dict())
            except CheckStillRunning:
                pass

        return check_outputs

    def _reply_check_outputs(self, check_outputs):
        """
        Put all available and collected check outputs on the output
        queue. The output queue is a `Queue` object shared between the
        `RadarClient` and `CheckManager` threads.

        :param check_outputs: A list of dictionaries containing check data outputs.
        """

        if len(check_outputs) > 0:
            self._output_queue.put_nowait(check_outputs)

    def _can_keep_running(self, check):
        """
        Return a boolean indicating if a check can keep running or not.

        :return: A boolean indicating if a check has not finished and
            is not overdue.
        """

        return not check.has_finished() and not check.is_overdue()

    def _terminate_overdue_checks(self):
        """
        Terminate all checks that exceeded their maximum execution time.
        """

        for check in self._execution_queue:
            if check.is_overdue():
                check.terminate()

    def _process_check_queues(self):
        """
        Move checks from the self._wait_queue to the self._execution queue only
        if there are any available slots in the self._execution_queue.
        """

        if self._available_slots():
            checks = self._wait_queue[:self._free_slots_amount()]
            self._wait_queue = self._wait_queue[self._free_slots_amount():]
            self._execution_queue.extend([check.run() for check in checks])
        else:
            self._terminate_overdue_checks()
            check_outputs = self._collect_outputs()
            self._execution_queue = [check for check in self._execution_queue if self._can_keep_running(check)]
            self._reply_check_outputs(check_outputs)

    def _terminate_all_checks(self):
        """
        Terminate all checks regardless they've finished or not.
        """

        for check in self._execution_queue:
            check.terminate()

    def _on_check(self, message):
        """
        Enqueue incoming checks for execution.

        :param message: A list of dictionaries containing checks data.
        """

        self._wait_queue.extend(self._build_checks(message))

    def _on_test(self, message):
        """
        Enqueue incoming checks for test execution. Currently the implementation
        of this method is exactly the same as the `_on_check` method.
        This implementation will change in the future.

        :param message: A list of dictionaries containing checks data.
        """
        self._on_check(message)

    def _log_action(self, message_type, check):
        """
        Log the action that is going to take place (TEST or CHECK), the source
        of the incoming message and the check to be run or tested.

        :param message_type: The type of the received message. Currently the
            message type is either TEST or CHECK.
        :param check: A dictionary containing check data.
        """

        RadarLogger.log("{} from {}:{} -> {}".format(
            RadarMessage.get_type(message_type), self._platform_setup.config['connect']['to'],
            self._platform_setup.config['connect']['port'], check))

    def _log_incoming_message(self, message_type, message):
        """
        Log all checks to be run or tested.

        :param message_type: The type of the received message. Currently the
            message type is either TEST or CHECK.
        :param message: A list of dictionaries containing checks data.
        """

        for check in message:
            self._log_action(message_type, check)

    def _process_message(self, message_type, message):
        """
        Process an incoming message by running the appropriate action.
        The currently implemented actions are check and test.

        :param message_type: The type of the received message. Currently the
            message type is either TEST or CHECK.
        :param message: A list of dictionaries containing checks data.
        """

        try:
            self._log_incoming_message(message_type, message)
            action = self._message_actions[message_type]
            action(message)
        except (KeyError, ValueError):
            RadarLogger.log("Error - Unknown message id {}. Message : {}.".format(message_type, message))

    def is_stopped(self):
        """
        Tell if the thread has been stopped.

        :return: A boolean indicating if the thread has been stopped.
        """

        return self.stop_event.is_set()

    def run(self):
        """
        Run the `CheckManager` thread.

        This method scans a `Queue` object continuously and if a new message
        arrives it is then processed (checks are put in a wait queue).

        If no new checks are pulled from the queue then we monitor that running
        checks (if any) don't exceed its maximum allowed execution time
        and collect the output from those who have finished.

        When the thread is stopped, all checks that are still running are
        terminated.
        """

        while not self.is_stopped():
            try:
                queue_message = self._input_queue.get_nowait()
                self._process_message(queue_message['message_type'], queue_message['message'])
            except EmptyQueue:
                self.stop_event.wait(self.STOP_EVENT_TIMEOUT)

            self._process_check_queues()

        self._terminate_all_checks()
