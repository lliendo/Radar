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
from radar.check import Check, CheckGroup, CheckError


class TestCheckGroup(TestCase):
    def test_check_group_default_values(self):
        check_group = CheckGroup(
            name='check group',
            checks=[
                Check(name='check 1', path='check_1'),
                Check(name='check 2', path='check_2')
            ]
        )
        self.assertEqual(type(check_group.checks), set)
        self.assertNotEqual(len(check_group.checks), 0)
        self.assertEqual(check_group.enabled, True)

    def test_check_group_does_not_contain_duplicates(self):
        check_group = CheckGroup(
            name='check group',
            checks=[
                Check(name='check 1', path='check_1'),
                Check(name='check 1', path='check_1')
            ]
        )
        self.assertEqual(len(check_group.checks), 1)

    def test_check_group_gets_updated(self):
        check = Check(name='check 1', path='check_1')
        check_group = CheckGroup(name='check group', checks=[check])
        updated = check_group.update_status({'id': check.id, 'status': Check.STATUS['OK']})
        self.assertEqual(updated, True)

    def test_check_does_not_get_updated(self):
        check = Check(name='check 1', path='check_1')
        check_group = CheckGroup(name='check group', checks=[check])
        updated = check_group.update_status({'id': check.id + 1, 'status': Check.STATUS['OK']})
        self.assertEqual(updated, False)

    def test_check_group_as_list(self):
        check_group = CheckGroup(
            name='check group',
            checks=[
                Check(name='check 1', path='check_1'),
                Check(name='check 2', path='check_2')
            ]
        )
        [self.assertEqual(type(c), Check) for c in check_group.as_list()]

    def test_check_groups_contains_different_checks(self):
        check = Check(name='Load average', path='load_average.py')
        another_check = Check(name='Free RAM', path='free_ram.py')
        check_group = CheckGroup(name='check group', checks=[check, another_check])
        self.assertEqual(len(check_group.checks), 2)

    def test_check_groups_are_equal(self):
        check = Check(name='Load average', path='load_average.py')
        another_check = Check(name='Free RAM', path='free_ram.py')
        check_group = CheckGroup(name='check group 1', checks=[check, another_check])
        another_check_group = CheckGroup(name='check group 1', checks=[another_check, check])
        self.assertEqual(check_group, another_check_group)

    def test_check_groups_are_not_equal(self):
        check = Check(name='Load average', path='load_average.py')
        another_check = Check(name='Free RAM', path='free_ram.py')
        self.assertNotEqual(CheckGroup(name='check group 1', checks=[check]), CheckGroup(name='check group 2', checks=[another_check]))

    def test_check_groups_set(self):
        check = Check(name='Load average', path='load_average.py')
        another_check = Check(name='Free RAM', path='free_ram.py')
        self.assertEqual(len(set([CheckGroup(name='check group 1', checks=[check, another_check]), CheckGroup(name='check group 1', checks=[check, another_check])])), 1)
        self.assertEqual(len(set([CheckGroup(name='check group 1', checks=[check]), CheckGroup(name='check group 2', checks=[another_check])])), 2)

    @raises(CheckError)
    def test_check_group_raises_exception_due_to_missing_id(self):
        check_group = CheckGroup(checks=[Check(name='check', path='check.py')])
        check_group.update_status({'status': Check.STATUS['OK']})

    @raises(CheckError)
    def test_check_group_raises_exception_due_to_missing_status(self):
        check = Check(name='check', path='check.py')
        check_group = CheckGroup(checks=[check])
        check_group.update_status({'id': check.id})
