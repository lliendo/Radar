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
from radar.misc import Switchable


class DummySwitch(Switchable):
    def __init__(self):
        self.some_attribute = 'a'
        self.some_other_attribute = 1
        super(DummySwitch, self).__init__()


class TestSwitchable(TestCase):
    def setUp(self):
        self.switchable = DummySwitch()

    def test_switchable_defaults(self):
        self.assertNotEqual(self.switchable.id, None)
        self.assertEqual(self.switchable.enabled, True)

    def test_switchable_disable(self):
        self.switchable.disable()
        self.assertEqual(self.switchable.enabled, False)

    def test_switchable_enable(self):
        self.switchable.disable()
        self.switchable.enable()
        self.assertEqual(self.switchable.enabled, True)

    def test_switchable_to_dict(self):
        d = self.switchable.to_dict(['some_attribute', 'some_other_attribute'])
        self.assertEqual(type(d), dict)
        self.assertEqual(type(d['some_attribute']), str)
        self.assertEqual(type(d['some_other_attribute']), int)
