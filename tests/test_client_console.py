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
from nose.tools import raises
from mock import Mock, MagicMock, patch
from json import loads as deserialize_json
from radar.console_client import RadarConsoleClientInput, RadarConsoleClientQuit, RadarConsoleClientEmptyInput, RadarConsoleClientError


class TestRadarConsoleClientInput(TestCase):
    def setUp(self):
        self.radar_console_client_input = RadarConsoleClientInput(Mock(), Mock())

    @raises(RadarConsoleClientQuit)
    def test_read_input_raises_quit_exception(self):
        with patch('__builtin__.raw_input', return_value='quit()'):
            self.radar_console_client_input._read_input()

    @raises(RadarConsoleClientEmptyInput)
    def test_read_input_raises_empty_input_exception(self):
        with patch('__builtin__.raw_input', return_value=''):
            self.radar_console_client_input._read_input()

    def test_write_output_queue_receives_valid_json(self):
        self.radar_console_client_input._write_output_queue('list()')
        called_args, _ = self.radar_console_client_input._output_queue.put.call_args_list[0]
        self.assertTrue('action' in deserialize_json(called_args[0]))

    @raises(RadarConsoleClientError)
    def test_read_input_queue_raises_exception_invalid_json(self):
        self.radar_console_client_input._input_queue.get = MagicMock(side_effect='{')
        self.radar_console_client_input._read_input_queue()

    @raises(RadarConsoleClientError)
    def test_read_input_queue_raises_exception_invalid_json_format_message_field_missing(self):
        self.radar_console_client_input._input_queue.get = MagicMock(side_effect='{}')
        self.radar_console_client_input._read_input_queue()

    @raises(RadarConsoleClientError)
    def test_read_input_queue_raises_exception_invalid_json_format_data_field_missing(self):
        self.radar_console_client_input._input_queue.get = MagicMock(side_effect='{"message": []}')
        self.radar_console_client_input._read_input_queue()
