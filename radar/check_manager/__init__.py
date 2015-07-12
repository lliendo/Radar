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
from ..check import Check
from ..protocol import Message


class CheckManager(Thread):

    STOP_EVENT_TIMEOUT = 0.2

    def __init__(self, platform_setup, input_queue, output_queue):
        Thread.__init__(self)
        self._platform_setup = platform_setup
        self._logger = platform_setup.logger
        self._input_queue = input_queue
        self._output_queue = output_queue
        self.stop_event = Event()
        self._message_actions = {
            Message.TYPE['CHECK']: self._on_check,
            Message.TYPE['TEST']: self._on_test,
        }

    def _build_checks(self, checks):
        return [Check(platform_setup=self._platform_setup, **c) for c in checks]

    def _on_check(self, message_type, message):
        checks = self._build_checks(message)
        self._run_checks(checks)

    def _on_test(self, message_type, message):
        checks = self._build_checks(message)
        self._run_checks(checks)

    def _process_message(self, message_type, message):
        try:
            action = self._message_actions[message_type]
            action(message_type, message)
        except KeyError:
            self._logger.log('Unknown message id \'{:}\'.'.format(message_type))

    def is_stopped(self):
        return self.stop_event.is_set()

    def _run_checks(self, checks):
        user = self._platform_setup.config['run as']['user']
        group = self._platform_setup.config['run as']['group']
        enforce_ownership = self._platform_setup.config['enforce ownership']
        checks_outputs = [c.run(user, group, enforce_ownership).to_check_reply_dict() for c in checks]
        self._output_queue.put_nowait(checks_outputs)

    def run(self):
        while not self.is_stopped():
            try:
                queue_message = self._input_queue.get_nowait()
                self._process_message(queue_message['message_type'], queue_message['message'])
            except EmptyQueue:
                self.stop_event.wait(self.STOP_EVENT_TIMEOUT)
