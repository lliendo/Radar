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
from mock import Mock, MagicMock, patch, ANY
from nose.tools import raises
from random import choice
from string import ascii_letters
from os import utime, remove
from os.path import dirname, join as join_path
from radar.check import UnixCheck, WindowsCheck, CheckError
from radar.logger import RadarLogger
from radar.config.client import ClientConfig
from . import platform_skip_test


class TestUnixCheck(TestCase):

    TESTS_DIR = dirname(__file__)

    def setUp(self):
        file_owner = self._get_random_string()
        self.test_filename = self._get_random_test_file_path()
        self.platform_setup = Mock()
        self.platform_setup.config = ClientConfig.DEFAULT_CONFIG
        self.platform_setup.config['checks'] = '/tmp'
        self.platform_setup.config['run as']['user'] = file_owner
        self.platform_setup.config['run as']['group'] = file_owner
        self.dummy_check = UnixCheck(name='dummy', path='dummy.py', platform_setup=self.platform_setup)
        RadarLogger._shared_state['logger'] = Mock()
        self._create_empty_file(self.test_filename)

    def _get_random_string(self, max_length=10):
        return ''.join(choice(ascii_letters) for _ in range(max_length))

    def _get_random_test_file_path(self):
        return join_path(self.TESTS_DIR, self._get_random_string())

    def _create_empty_file(self, filename):
        try:
            utime(filename, None)
        except Exception:
            open(filename, 'a').close()

    def _delete_empty_file(self, filename):
        try:
            remove(filename)
        except Exception:
            pass

    @platform_skip_test('Windows')
    @raises(CheckError)
    def test_owned_by_stated_user_raises_error_if_inexistent_file(self):
        self.dummy_check._owned_by_stated_user(self.test_filename)

    @platform_skip_test('Windows')
    @raises(CheckError)
    def test_owned_by_user_raises_error_if_inexistent_user(self):
        self.dummy_check._owned_by_stated_user(self.test_filename)

    @platform_skip_test('Windows')
    @raises(CheckError)
    def test_owned_by_group_raises_error_if_inexistent_group(self):
        self.dummy_check._owned_by_user = MagicMock(return_value=True)
        self.dummy_check._owned_by_stated_user(self.test_filename)

    @platform_skip_test('Windows')
    @raises(CheckError)
    def test_windows_check_raises_error_when_instantiated_on_unix(self):
        WindowsCheck(name='dummy', path='dummy.py', platform_setup=self.platform_setup)

    def tearDown(self):
        self._delete_empty_file(self.test_filename)
