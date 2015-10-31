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
from yaml import load
from mock import patch
from radar.config import ConfigError
from radar.config.server import CheckGroupBuilder
from radar.check import Check


class TestCheckBuilder(TestCase):
    def test_repeated_checks_group_are_excluded(self):
        input_yaml = """
        - check group:
            name: A
            checks:
                - check:
                    name: B
                    path: B
                    args: B

                - check:
                    name: C
                    path: C
                    args: C

        - check group:
            name: A
            checks:
                - check:
                    name: B
                    path: B
                    args: B

                - check:
                    name: C
                    path: C
                    args: C

        """

        checks = [
            Check(name='B', path='B', args='B'),
            Check(name='C', path='C', args='C'),
        ]

        with patch.object(CheckGroupBuilder, '_read_config', return_value=load(input_yaml)):
            check_group = CheckGroupBuilder(None).build(checks)
            self.assertEqual(len(check_group), 1)
            self.assertTrue(checks[0] in check_group[0].checks)
            self.assertTrue(checks[1] in check_group[0].checks)

    def test_check_is_referenced(self):
        input_yaml = """
        - check group:
            name: A
            checks:
                - check:
                    name: B
        """

        check = Check(name='B', path='B', args='B')

        with patch.object(CheckGroupBuilder, '_read_config', return_value=load(input_yaml)):
            check_group = CheckGroupBuilder(None).build([check])
            self.assertEqual(len(check_group[0].checks), 1)
            self.assertTrue(check in check_group[0].checks)

    @raises(ConfigError)
    def test_non_existent_check_raises_config_error(self):
        input_yaml = """
        - check group:
            name: A
            checks:
                - check:
                    name: C
        """

        with patch.object(CheckGroupBuilder, '_read_config', return_value=load(input_yaml)):
            CheckGroupBuilder(None).build([])

    @raises(ConfigError)
    def test_wrong_yaml_format_raises_error(self):
        input_yaml = """
        - check group:
        """

        with patch.object(CheckGroupBuilder, '_read_config', return_value=load(input_yaml)):
            CheckGroupBuilder(None).build([Check(name='B', path='B', args='B')])
