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
from mock import patch
from yaml import load
from radar.config import ConfigError
from radar.config.server import ContactBuilder


class TestContactBuilder(TestCase):
    def test_repeated_contacts_are_excluded(self):
        input_yaml = """
        - contact:
            name: A
            email: A

        - contact:
            name: A
            email: A
        """

        with patch.object(ContactBuilder, '_read_config', return_value=load(input_yaml)):
            self.assertEqual(len(ContactBuilder(None).build()), 1)

    @raises(ConfigError)
    def _test_raises_config_error(self, input_yaml):
        with patch.object(ContactBuilder, '_read_config', return_value=load(input_yaml)):
            ContactBuilder(None).build()

    def test_missing_name_raises_config_error(self):
        input_yaml = """
        - contact:
            email: A
        """

        self._test_raises_config_error(input_yaml)

    def test_missing_email_raises_config_error(self):
        input_yaml = """
        - contact:
            name: A
        """

        self._test_raises_config_error(input_yaml)
