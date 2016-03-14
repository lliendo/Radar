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


from unittest.case import SkipTest
from radar.platform_setup import Platform


# This decorator allows us to perform a test only if the platform specified by
# ourselves matches the detected platform.
class platform_skip_test(object):
    def __init__(self, selected_platform):
        self._selected_platform = selected_platform

    # The closure name has to be 'test_...' otherwise it does not get executed
    # by Nose.
    def __call__(self, f):
        def test_wrapper(*wrapped_f_args, **wrapped_f_kwargs):
            return f(*wrapped_f_args, **wrapped_f_kwargs)

        if Platform.get_platform_type() == self._selected_platform:
            raise SkipTest()

        return test_wrapper
