#!/usr/bin/env python

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


from shlex import split as split_args
from subprocess import call
from argparse import ArgumentParser


class DocBuilderError(Exception):
    pass


class DocBuilder(object):

    DEFAULT_LANG = 'en'
    SUPPORTED_LANGS = [DEFAULT_LANG, 'es']

    SPHINX_DIRS = {
        'output': '_build/html',
        'locale_outout': '_build/locale',
        'doctree_output': '_build/doctrees',
    }

    def _build_parser(self):
        parser = ArgumentParser()
        parser.add_argument('-l', '--language', dest='lang', action='store', default=self.DEFAULT_LANG, required=False)

        return parser

    def _build_default_lang_docs(self):
        call(split_args('sphinx-build -b html -d _build/doctrees . _build/html'))

    def _build_non_default_lang_docs(self, lang):
        call(split_args('sphinx-build -b gettext . _build/locale'))
        call(split_args('sphinx-intl update -p _build/locale -l {:}'.format(lang)))
        call(split_args('sphinx-intl build'))
        call(split_args('sphinx-build -b html -d _build/doctrees -D language=\'{:}\' . _build/html'.format(lang)))

    def _build_docs(self, lang):
        if lang not in self.SUPPORTED_LANGS:
            raise DocBuilderError('Error - Language \'{:}\' is not currently supported.'.format(lang))

        if lang == self.DEFAULT_LANG:
            self._build_default_lang_docs()
        else:
            self._build_non_default_lang_docs(lang)

    def build(self):
        options = self._build_parser().parse_args()
        self._build_docs(options.lang)


if __name__ == '__main__':
    try:
        DocBuilder().build()
    except Exception, e:
        print e
