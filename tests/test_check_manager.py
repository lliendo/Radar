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


from unittest import TestCase
from mock import Mock, MagicMock, ANY
from nose.tools import raises
from radar.logger import RadarLogger
from radar.check import CheckError
from radar.check_manager import CheckManager
from radar.check import Check, CheckError
from radar.protocol import RadarMessage
from radar.config.client import ClientConfig


class TestCheckManager(TestCase):
    def setUp(self):
        self.platform_setup = Mock()
        self.platform_setup.config = ClientConfig.DEFAULT_CONFIG
        self.platform_setup.config['check concurrency'] = 2
        self.check_manager = CheckManager(self.platform_setup, Mock(), Mock())
        self.check_manager._output_queue = Mock()
        RadarLogger._shared_state['logger'] = Mock()

    def test_process_message_fails_due_to_invalid_message_type(self):
        self.check_manager._process_message(max(RadarMessage.TYPE.values()) + 1, [{}])
        RadarLogger._shared_state['logger'].info.assert_called_with(ANY)

    def test_process_message_fails_due_to_invalid_check_sent_from_server(self):
        self.check_manager._process_message(RadarMessage.TYPE['CHECK'], [{}])
        RadarLogger._shared_state['logger'].info.assert_called_with(ANY)

    @raises(CheckError)
    def test_build_checks_raises_check_error(self):
        self.check_manager._build_checks([{}])

    def _build_check(self, output='{}', has_finished=False, is_overdue=False):
        process_handler = Mock()
        process_handler.communicate = MagicMock(return_value=(output, '', ''))

        check = Check(name='dummy', path='dummy.py', platform_setup=self.platform_setup)
        check._call_popen = MagicMock(return_value=process_handler)
        check.has_finished = MagicMock(return_value=has_finished)
        check._terminate = MagicMock()

        return check

    def _build_checks(self, checks_config):
        return [self._build_check(**check_config) for check_config in checks_config]

    def test_process_check_queues(self):
        checks_config = [
            {'output': '{"status": "OK"}'},
            {'output': '{"status": "WARNING"}'},
            {'output': '{"status": "SEVERE"}'},
        ]

        checks = self._build_checks(checks_config)
        self.check_manager._wait_queue.extend(checks)
        self.check_manager._process_check_queues()
        self.assertEqual(
            len(self.check_manager._wait_queue),
            len(checks_config) - self.platform_setup.config['check concurrency']
        )
        self.assertEqual(len(self.check_manager._execution_queue), self.platform_setup.config['check concurrency'])

        # Let's assume all checks finished gracefully on time.
        # for check in self.check_manager._execution_queue:
        for check in checks:
            check.has_finished = MagicMock(return_value=True)

        self.check_manager._process_check_queues()
        self.assertEqual(
            len(self.check_manager._wait_queue),
            len(checks_config) - self.platform_setup.config['check concurrency']
        )
        self.assertEqual(len(self.check_manager._execution_queue), 0)

        # Let's make sure that all outputs are replied to the output queue
        # with their respective status.
        called_args, _ = self.check_manager._output_queue.put_nowait.call_args_list[0]
        self.assertEqual(len(called_args[0]), self.platform_setup.config['check concurrency'])
        statuses = [output['status'] for output in called_args[0]]
        self.assertTrue(Check.STATUS['OK'] in statuses)
        self.assertTrue(Check.STATUS['WARNING'] in statuses)

    def test_process_check_queue_with_overdue_check(self):
        checks_config = [
            {'output': '{"status": "OK"}'},
            {'output': '{"status": "WARNING"}'},
            {'output': '{"status": "SEVERE"}'},
        ]
        checks = self._build_checks(checks_config)
        self.check_manager._wait_queue.extend(checks)

        self.check_manager._process_check_queues()
        self.assertEqual(len(self.check_manager._wait_queue), 1)
        self.assertEqual(len(self.check_manager._execution_queue), 2)

        checks[0].has_finished = MagicMock(return_value=True)

        # We assume a check was terminated because the timeout was reached.
        checks[1].is_overdue = MagicMock(return_value=True)
        checks[1].has_finished = MagicMock(return_value=True)

        self.check_manager._process_check_queues()
        self.assertTrue(checks[1]._terminate.called)
        self.assertEqual(len(self.check_manager._wait_queue), 1)
        self.assertEqual(len(self.check_manager._execution_queue), 0)

        # Let's make sure that all outputs are replied to the output queue and
        # that one of them has a TIMEOUT status.
        called_args, _ = self.check_manager._output_queue.put_nowait.call_args_list[0]
        self.assertEqual(len(called_args[0]), 2)
        statuses = [output['status'] for output in called_args[0]]
        self.assertTrue(Check.STATUS['OK'] in statuses)
        self.assertTrue(Check.STATUS['TIMEOUT'] in statuses)
