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

Copyright 2015 Lucas Liendo.
"""


from Queue import Empty as EmptyQueue
from threading import Thread, Event
from ..logger import RadarLogger
from ..check import UnixCheck, WindowsCheck, CheckError
from ..protocol import Message
from ..platform_setup import Platform


class CheckManagerError(Exception):
    pass


class CheckManager(Thread):

    STOP_EVENT_TIMEOUT = 0.2
    AVAILABLE_PLATFORMS = {
        'UNIX': UnixCheck,
        'Windows': WindowsCheck,
    }

    def __init__(self, platform_setup, input_queue, output_queue, stop_event=None):
        Thread.__init__(self)
        self._platform_setup = platform_setup
        self._input_queue = input_queue
        self._output_queue = output_queue
        self.stop_event = stop_event or Event()
        self._Check = self._get_platform_check_class()
        self._message_actions = {
            Message.TYPE['CHECK']: self._on_check,
            Message.TYPE['TEST']: self._on_test,
        }

    def _get_platform_check_class(self):
        platform = Platform.get_platform_type()

        try:
            return self.AVAILABLE_PLATFORMS[platform]
        except KeyError:
            raise CheckManagerError('Error - Platform : \'{:}\' is not available.'.format(platform))

    def _build_checks(self, checks):
        try:
            return [self._Check(name=c['path'], platform_setup=self._platform_setup, **c) for c in checks]
        except KeyError:
            raise CheckError('Error - Server sent empty or invalid check.')

    def _on_check(self, message):
        self._run_checks(self._build_checks(message))

    # Yes, is the same as above ! This implementation may change in the future.
    def _on_test(self, message):
        self._on_check(message)

    def _log_action(self, message_type, check):
        RadarLogger.log('{:} from {:}:{:} -> {:}'.format(
            Message.get_type(message_type), self._platform_setup.config['connect']['to'],
            self._platform_setup.config['connect']['port'], check)
        )

    def _log_incoming_message(self, message_type, message):
        [self._log_action(message_type, check) for check in message]

    def _process_message(self, message_type, message):
        try:
            self._log_incoming_message(message_type, message)
            action = self._message_actions[message_type]
            action(message)
        except (KeyError, ValueError):
            RadarLogger.log('Error - Unknown message id {:}. Message : {:}.'.format(message_type, message))
        except CheckError as e:
            RadarLogger.log(e)

    def is_stopped(self):
        return self.stop_event.is_set()

    def _run_checks(self, checks):
        checks_outputs = [c.run().to_check_reply_dict() for c in checks]
        self._output_queue.put_nowait(checks_outputs)

    def run(self):
        while not self.is_stopped():
            try:
                queue_message = self._input_queue.get_nowait()
                self._process_message(queue_message['message_type'], queue_message['message'])
            except EmptyQueue:
                self.stop_event.wait(self.STOP_EVENT_TIMEOUT)
