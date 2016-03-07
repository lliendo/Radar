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
from yaml import load
from mock import patch
from radar.config import ConfigBuilder


class GenericConfigBuilder(ConfigBuilder):
    pass


class TestConfigBuilder(TestCase):
    def test_config_dict_gets_lower_cased(self):
        input_yaml = """
        - ELEMENT:
            ID: A

        - COMPOSITE ELEMENT:
            ID: B
            ELEMENTS:
                - ELEMENT:
                    ID: C
                - ELEMENT:
                    ID: D
        """

        element = {'element': {'id': 'A'}}
        composite_element = {
            'composite element': {
                'id': 'B',
                'elements': [
                    {'element': {'id': 'C'}},
                    {'element': {'id': 'D'}},
                ]
            }
        }

        with patch.object(GenericConfigBuilder, '_read_config', return_value=load(input_yaml)):
            config_builder = GenericConfigBuilder(None)
            self.assertEqual([element, composite_element], config_builder.config)

    def test_config_dict_merges_options(self):
        input_yaml = """
            option:
                key1: overridden

            another option:
                key4: overridden
        """

        default_config = {
            'option': {'key1': 'value', 'key2': 'value2'},
            'another option': {'key3': 'value3', 'key4': 'value4'}
        }

        with patch.object(GenericConfigBuilder, '_read_config', return_value=load(input_yaml)):
            config_builder = GenericConfigBuilder(None)
            config_builder.merge_config(default_config)
            self.assertEqual(config_builder.config['option']['key1'], 'overridden')
            self.assertEqual(config_builder.config['another option']['key4'], 'overridden')
