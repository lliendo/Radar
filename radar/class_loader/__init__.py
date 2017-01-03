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

Copyright 2015 - 2017 Lucas Liendo.
"""


from io import open as io_open
from os.path import join as join_path
from ast import parse as ast_parse, walk as ast_walk, ClassDef
from pkgutil import iter_modules
from sys import path as module_search_path
from ..logger import RadarLogger


class ClassLoaderError(Exception):
    pass


class ClassLoader(object):
    """
    This class offers a simple mechanism to get all user-defined classes from
    an external Python module. This is useful if you want to load unknown classes
    dynamically at run-time.

    :param module_path: The path to a Python module.
    """

    ENCODING_DECLARATION = '# -*- coding: utf-8 -*-'

    def __init__(self, module_path):
        self._module_path = module_path
        module_search_path.append(module_path)

    def _get_class_names(self, filename):
        """
        Parse Python source code from a file and return all defined classes.

        :param filename: Path to a file containing Python code.
        :return: A list containing class names.
        """

        class_names = []

        try:
            with io_open(filename) as fd:
                # We remove the encoding declaration, otherwise file parsing fails.
                parsed_source = ast_parse(fd.read().strip(self.ENCODING_DECLARATION))
                class_names = [node.name for node in ast_walk(parsed_source) if isinstance(node, ClassDef)]
        except IOError as error:
            raise ClassLoaderError("Error - Couldn't open : '{}'. Reason : {}.".format(filename, error.strerror))
        except SyntaxError as error:
            raise ClassLoaderError("Error - Couldn't parse '{}'. Reason: {}.".format(filename, error))

        return class_names

    def get_classes(self, subclass=object):
        """
        Retrieve all classes defined in a Python module.

        Only all classes defined in `__init__.py` are read and made
        available to Radar. Classes defined outside `__init__.py` are not
        scanned at all.

        :param subclass: Indicates which subclasses should be read.
            By default all subclasses (`object` subclasses) are read.
        :return: A list containing loaded classes from a Python module.
        """

        loaded_classes = []

        for _, module_name, _ in iter_modules(path=[self._module_path]):
            module_path = join_path(self._module_path, module_name)

            try:
                # We only get classes defined in '__init__.py'. Classes defined in other
                # files within a module are not brought to the Radar namespace.
                class_names = self._get_class_names(module_path + '/__init__.py')
                imported_module = __import__(module_name)
                loaded_classes += [getattr(imported_module, class_name) for class_name in class_names]
            except ClassLoaderError as error:
                RadarLogger.log(error)

        return [loaded_class for loaded_class in loaded_classes if issubclass(loaded_class, subclass)]
