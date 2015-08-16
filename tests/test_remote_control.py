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
from radar.misc import Switch


class DummySwitch(Switch):
    def __init__(self):
        self.some_attribute = 'a'
        self.some_other_attribute = 1
        super(DummySwitch, self).__init__()


class TestSwitch(TestCase):
    def setUp(self):
        self.remote_control = DummySwitch()

    def test_remote_control_default_instance(self):
        self.assertNotEqual(self.remote_control.id, None)
        self.assertEqual(self.remote_control.enabled, True)

    def test_remote_control_disable(self):
        self.remote_control.disable()
        self.assertEqual(self.remote_control.enabled, False)

    def test_remote_control_enable(self):
        self.remote_control.disable()
        self.remote_control.enable()
        self.assertEqual(self.remote_control.enabled, True)

    def test_remote_control_to_dict(self):
        d = self.remote_control.to_dict(['some_attribute', 'some_other_attribute'])
        self.assertEqual(type(d), dict)
        self.assertEqual(type(d['some_attribute']), str)
        self.assertEqual(type(d['some_other_attribute']), int)
