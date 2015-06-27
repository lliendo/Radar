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


from os.path import join as join_path
from ast import parse as ast_parse
from ast import walk as ast_walk
from ast import ClassDef
from pkgutil import iter_modules
from sys import path as module_search_path


class ClassLoaderError(Exception):
    pass


class ClassLoader(object):
    """
    This class offers a simple mechanism to get all user-defined
    classes from an external module. This is useful if you want
    to load unknown classes dynamically at run-time.
    """

    def __init__(self, module_path):
        self._module_path = module_path
        module_search_path.append(module_path)

    def _get_class_names(self, file):
        try:
            with open(file) as fd:
                parsed_source = ast_parse(fd.read())
                class_names = [n.name for n in ast_walk(parsed_source) if isinstance(n, ClassDef)]
        except IOError, e:
            raise ClassLoaderError('Error - Couldn\'t open : \'{:}\'. Reason : {:}'.format(file, e.strerror))

        return class_names

    def get_classes(self, subclass=object):
        classes = []

        for _, module_name, _ in iter_modules(path=[self._module_path]):
            module_path = join_path(self._module_path, module_name)
            class_names = self._get_class_names(module_path + '/__init__.py')
            imported_module = __import__(module_name)
            classes += [getattr(imported_module, class_name) for class_name in class_names]

        return [C for C in classes if issubclass(C, subclass)]
