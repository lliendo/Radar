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
from mock import Mock, ANY
from nose.tools import raises
from radar.check import CheckError
from radar.check_manager import CheckManager
from radar.protocol import Message


class TestCheckManager(TestCase):
    def setUp(self):
        self.platform_setup = Mock()
        self.platform_setup.config = {
            'connect': {
                'to': ANY,
                'port': ANY,
            }
        }

    def test_process_message_fails_due_to_invalid_message_type(self):
        check_manager = CheckManager(self.platform_setup, Mock(), Mock())
        check_manager._logger = Mock()
        check_manager._process_message(max(Message.TYPE.values()) + 1, [{}])
        check_manager._logger.log.assert_called_with(ANY)

    def test_process_message_fails_due_to_invalid_check_sent_from_server(self):
        check_manager = CheckManager(self.platform_setup, Mock(), Mock())
        check_manager._logger = Mock()
        check_manager._process_message(Message.TYPE['CHECK'], [{}])
        # TODO: Fix to assert a CheckError instance is passed to 'log'. Why does this fail ?
        # check_manager._logger.log.assert_called_with(CheckError('Error - Server sent empty or invalid check.'))
        check_manager._logger.log.assert_called_with(ANY)

    @raises(CheckError)
    def test_build_checks_raises_check_error(self):
        check_manager = CheckManager(self.platform_setup, Mock(), Mock())
        check_manager._build_checks([{}])
