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
from mock import Mock, MagicMock
from nose.tools import raises
from json import dumps as serialize_json
from radar.check import Check, CheckError


class TestCheck(TestCase):
    def setUp(self):
        self.dummy_check = Check(name='dummy', path='dummy.py')

    def test_check_default_values(self):
        self.assertNotEqual(self.dummy_check.id, None)
        self.assertEqual(self.dummy_check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.dummy_check.current_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.dummy_check.enabled, True)

    @raises(CheckError)
    def test_check_must_have_a_name(self):
        Check(path='dummy.py')

    @raises(CheckError)
    def test_check_must_have_a_path(self):
        Check(name='dummy')

    def test_check_gets_updated(self):
        new_status = {
            'id': self.dummy_check.id,
            'status': Check.STATUS['OK'],
            'details': 'details',
            'data': {
                'some data'
            },
        }

        self.assertEqual(self.dummy_check.update_status(new_status), True)
        self.assertEqual(self.dummy_check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.dummy_check.current_status, Check.STATUS['OK'])
        self.assertEqual(self.dummy_check.details, 'details')
        self.assertEqual(self.dummy_check.data, {'some data'})

    def test_check_does_not_get_updated_if_id_does_not_match(self):
        new_status = {
            'id': self.dummy_check.id + 1,
            'status': Check.STATUS['OK'],
        }

        self.assertEqual(self.dummy_check.update_status(new_status), False)
        self.assertEqual(self.dummy_check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.dummy_check.current_status, Check.STATUS['UNKNOWN'])

    def test_check_does_not_get_updated_when_disabled(self):
        new_status = {
            'id': self.dummy_check.id,
            'status': Check.STATUS['OK'],
        }

        self.dummy_check.disable()
        self.assertEqual(self.dummy_check.update_status(new_status), False)
        self.assertEqual(self.dummy_check.previous_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(self.dummy_check.current_status, Check.STATUS['UNKNOWN'])

    @raises(CheckError)
    def test_check_raises_exception_when_updating_status_if_missing_id(self):
        self.dummy_check.update_status({'status': Check.STATUS['OK']})

    @raises(CheckError)
    def test_check_raises_exception_when_updating_status_if_missing_status(self):
        self.dummy_check.update_status({'id': self.dummy_check.id})

    @raises(CheckError)
    def test_check_raises_exception_if_invalid_status_beyond_lowest_status(self):
        self.dummy_check.update_status({'status': min(Check.STATUS.values()) - 1})

    @raises(CheckError)
    def test_check_raises_exception_if_invalid_status_beyond_highest_status(self):
        self.dummy_check.update_status({'status': max(Check.STATUS.values()) + 1})

    @raises(CheckError)
    def test_get_status_exception_due_to_invalid_status_beyond_lowest_status(self):
        self.dummy_check.get_status(min(Check.STATUS.values()) - 1)

    @raises(CheckError)
    def test_get_status_exception_due_to_invalid_status_beyond_highest_status(self):
        self.dummy_check.get_status(max(Check.STATUS.values()) + 1)

    def test_deserialize_output(self):
        d = self.dummy_check._deserialize_output(serialize_json({'status': 'ok'}))
        self.assertEqual(d['status'], Check.STATUS['OK'])

    def test_deserialize_output_does_not_contain_any_arbitrary_field(self):
        d = self.dummy_check._deserialize_output(serialize_json({'status': 'ok', 'field': 'value'}))
        self.assertEqual(d['status'], Check.STATUS['OK'])
        self.assertTrue('field' not in d)

    @raises(CheckError)
    def test_deserialize_status_raises_exception_if_invalid_status(self):
        self.dummy_check._deserialize_output(serialize_json({'status': 'INVALID STATUS'}))

    @raises(CheckError)
    def test_deserialize_status_raises_exception_if_missing_status(self):
        self.dummy_check._deserialize_output(serialize_json({'details': 'details'}))

    @raises(CheckError)
    def test_deserialize_status_raises_exception_if_invalid_json(self):
        self.dummy_check._deserialize_output('{')

    def test_checks_are_equal(self):
        self.assertEqual(self.dummy_check, Check(name='dummy', path='dummy.py'))

    def test_checks_are_not_equal(self):
        load_average_check = Check(name='Load average', path='load-average.py')
        self.assertNotEqual(self.dummy_check, load_average_check)

    def _assert_dictionary_contains_keys(self, d, expected_keys):
        self.assertTrue(all([k in d for k in expected_keys]))
        self.assertEqual(len(d.keys()), len(expected_keys))

    def test_to_dict(self):
        d = self.dummy_check.to_dict()
        expected_keys = ['id', 'name', 'path', 'args', 'current_status', 'previous_status', 'details', 'data', 'enabled']
        self._assert_dictionary_contains_keys(d, expected_keys)

    def test_to_check_dict(self):
        d = Check(name='dummy', path='dummy.py', args='-a argument').to_check_dict().pop()
        expected_keys = ['id', 'path', 'args']
        self._assert_dictionary_contains_keys(d, expected_keys)

    def test_to_check_dict_does_not_contain_args(self):
        d = Check(name='dummy', path='dummy.py').to_check_dict().pop()
        self.assertTrue('args' not in d)

    def test_to_check_reply_dict(self):
        d = Check(name='dummy', path='dummy.py').to_check_reply_dict()
        expected_keys = ['id', 'status']
        self._assert_dictionary_contains_keys(d, expected_keys)

    def test_to_check_reply_dict_contains_details(self):
        d = Check(name='dummy', path='dummy.py', details='details').to_check_reply_dict()
        self.assertTrue('details' in d)

    def test_to_check_reply_dict_contains_data(self):
        d = Check(name='dummy', path='dummy.py', data={'data': 'some data'}).to_check_reply_dict()
        self.assertTrue('data' in d)

    def test_check_as_list(self):
        self.assertEqual(type(self.dummy_check.as_list()), list)
        self.assertEqual(len(self.dummy_check.as_list()), 1)

    def test_check_set(self):
        duplicated_dummy_check = Check(name='dummy', path='dummy.py')
        another_check = Check(name='Free RAM', path='free-ram.py')
        self.assertEqual(len(set([self.dummy_check, duplicated_dummy_check])), 1)
        self.assertEqual(len(set([self.dummy_check, another_check])), 2)
        self.assertEqual(len(set([self.dummy_check, duplicated_dummy_check, another_check])), 2)

    def test_build_absolute_path_given_a_relative_path(self):
        platform_setup_mock = Mock()
        platform_setup_mock.PLATFORM_CONFIG = {'checks': '/tmp'}
        dummy_check = Check(name='dummy', path='dummy.py', platform_setup=platform_setup_mock)
        self.assertEqual(dummy_check._build_absolute_path(), ['/tmp/dummy.py'])

    def test_build_absolute_path_given_an_absolute_path(self):
        platform_setup_mock = Mock()
        platform_setup_mock.PLATFORM_CONFIG = {'checks': '/tmp'}
        absolute_check_path = '/usr/local/radar/client/checks/dummy.py'
        dummy_check = Check(name='dummy', path=absolute_check_path, platform_setup=platform_setup_mock)
        self.assertEqual(dummy_check._build_absolute_path(), [absolute_check_path])

    def test_run_fails(self):
        dummy_check = Check(name='dummy', path='dummy.py', platform_setup=Mock())
        dummy_check._call_popen = MagicMock(return_value='{}')
        dummy_check.run()
        self.assertEqual(dummy_check.current_status, Check.STATUS['ERROR'])
        self.assertEqual(dummy_check.previous_status, Check.STATUS['UNKNOWN'])

    def test_run(self):
        dummy_check = Check(name='dummy', path='dummy.py', platform_setup=Mock())
        dummy_check._call_popen = MagicMock(return_value='{"status": "OK"}')
        dummy_check.run()
        self.assertEqual(dummy_check.current_status, Check.STATUS['OK'])
        self.assertEqual(dummy_check.previous_status, Check.STATUS['UNKNOWN'])
