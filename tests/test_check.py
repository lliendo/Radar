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
from json import dumps as serialize_json
from radar.check import Check, CheckError


class TestCheck(TestCase):
    def setUp(self):
        self.check = Check(name='check', path='check.py')

    def test_check_default_values(self):
        self.assertNotEqual(self.check.id, None)
        self.assertEqual(self.check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.check.current_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.check.enabled, True)

    def test_check_gets_updated(self):
        new_status = {
            'id': self.check.id,
            'status': Check.STATUS['OK']
        }
        self.assertEqual(self.check.update_status(new_status), True)
        self.assertEqual(self.check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.check.current_status, Check.STATUS['OK'])

        self.assertEqual(self.check.update_status(new_status), True)
        self.assertEqual(self.check.previous_status, Check.STATUS['OK'])
        self.assertEqual(self.check.current_status, Check.STATUS['OK'])

    def test_check_details_gets_updated(self):
        new_status = {
            'id': self.check.id,
            'status': Check.STATUS['OK'],
            'details': 'details',
        }
        self.assertEqual(self.check.update_status(new_status), True)
        self.assertEqual(self.check.details, 'details')

    def test_check_data_gets_updated(self):
        new_status = {
            'id': self.check.id,
            'status': Check.STATUS['OK'],
            'data': {'some data'},
        }
        self.assertEqual(self.check.update_status(new_status), True)
        self.assertEqual(self.check.data, {'some data'})

    def test_check_does_not_get_updated_invalid_id(self):
        new_status = {
            'id': self.check.id + 1,
            'status': Check.STATUS['OK'],
        }
        self.assertEqual(self.check.update_status(new_status), False)
        self.assertEqual(self.check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.check.current_status, Check.STATUS['UNKNOWN'])

    def test_check_does_not_get_updated_check_is_disabled(self):
        new_status = {
            'id': self.check.id,
            'status': Check.STATUS['OK'],
        }
        self.check.disable()
        self.assertEqual(self.check.update_status(new_status), False)
        self.assertEqual(self.check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.check.current_status, Check.STATUS['UNKNOWN'])

    @raises(CheckError)
    def test_check_raises_exception_due_to_missing_id(self):
        Check(name='check', path='check.py').update_status({'status': Check.STATUS['OK']})

    @raises(CheckError)
    def test_check_raises_exception_due_to_missing_status(self):
        self.check.update_status({'id': self.check.id})

    @raises(CheckError)
    def test_check_raises_exception_due_to_invalid_status_beyond_lowest_status(self):
        self.check.update_status({'status': Check.STATUS['ERROR'] - 1})

    @raises(CheckError)
    def test_check_raises_exception_due_to_invalid_status_beyond_highest_status(self):
        self.check.update_status({'status': Check.STATUS['TIMEOUT'] + 1})

    def test_get_status(self):
        [self.check.get_status(v) for v in Check.STATUS.values()]

    @raises(CheckError)
    def test_get_status_exception_due_to_invalid_status_beyond_lowest_status(self):
        self.check.get_status(min(Check.STATUS.values()) - 1)

    @raises(CheckError)
    def test_get_status_exception_due_to_invalid_status_beyond_highest_status(self):
        self.check.get_status(max(Check.STATUS.values()) + 1)

    def test_deserialize_output(self):
        output = serialize_json({'status': 'ok'})
        d = self.check._deserialize_output(output)
        self.assertEqual(type(d), dict)
        self.assertEqual(d['status'], Check.STATUS['OK'])

    @raises(CheckError)
    def test_deserialize_status_raises_exception_due_to_invalid_status(self):
        self.check._deserialize_output(serialize_json({'status': 'invalid status'}))

    @raises(CheckError)
    def test_deserialize_status_raises_exception_due_to_missing_status(self):
        self.check._deserialize_output(serialize_json({}))

    @raises(CheckError)
    def test_deserialize_status_raises_exception_due_to_invalid_json(self):
        self.check._deserialize_output('{')

    def test_checks_are_equal(self):
        self.assertEqual(self.check, Check(name='check', path='check.py'))

    def test_checks_are_not_equal(self):
        check = Check(name='Load average', path='load_average.py')
        another_check = Check(name='Free RAM', path='free_ram.py')
        self.assertNotEqual(check, another_check)

    def test_to_dict(self):
        d = Check(name='check', path='check.py').to_dict()
        keys = ['id', 'name', 'path', 'args', 'current_status', 'previous_status', 'details', 'data', 'enabled']
        self.assertTrue(all([k in d for k in keys]))

    def test_to_check_dict(self):
        d = Check(name='check', path='check.py').to_check_dict().pop()
        self.assertTrue(all([k in d for k in ['id', 'path']]))

    def test_to_check_dict_contains_args(self):
        d = Check(name='check', path='check.py', args='-a argument').to_check_dict().pop()
        self.assertTrue('args' in d)

    def test_to_check_reply_dict(self):
        d = Check(name='check', path='check.py').to_check_reply_dict()
        self.assertTrue(all([k in d for k in ['id', 'status']]))

    def test_to_check_reply_dict_contains_details(self):
        d = Check(name='check', path='check.py', details='details').to_check_reply_dict()
        self.assertTrue('details' in d)

    def test_to_check_reply_dict_contains_data(self):
        d = Check(name='check', path='check.py', data={'data': 'some data'}).to_check_reply_dict()
        self.assertTrue('data' in d)

    def test_check_as_list(self):
        self.assertEqual(type(self.check.as_list()), list)
        self.assertEqual(len(self.check.as_list()), 1)

    def test_check_set(self):
        check = Check(name='Load average', path='load_average', args='-a arg')
        duplicated_check = Check(name='Load average', path='load_average', args='-a arg')
        another_check = Check(name='Free RAM', path='free_ram', args='-a arg')
        self.assertEqual(len(set([check, duplicated_check])), 1)
        self.assertEqual(len(set([check, another_check])), 2)
        self.assertEqual(len(set([check, duplicated_check, another_check])), 2)
