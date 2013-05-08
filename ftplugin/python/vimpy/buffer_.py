# -*- coding: utf-8 -*-
# dydrmntion@gmail.com ~ 2013

import re
import logging

import vim

from util import ModuleImporter

logger = logging.getLogger(__name__)


BANG_LINE = 'bang'

WHITE_LINE = 'whiteline'

IMPORT_LINE = 'import'

IMPORT_FROM = 'import_from'

IMPORT_DIRECT = 'import_direct'

CODE_LINE = 'code_line'


class VimBuffer(object):
    '''Representation of the current vim buffer'''

    _lines = []

    def __init__(self):

        self._read_buffer()

    def __getitem__(self, key):
        try:
            return self._lines[key]
        except IndexError:
            return self._lines[-1]

    def __len__(self):
        return len(self._lines)

    @property
    def import_lines(self):
        return [l for l in self._lines if l['type'] is IMPORT_LINE]

    def _read_buffer(self):

        self._lines = []

        rgx = re.compile(r'^(?:(?P<bang>#.*)|(?P<whiteline>\s*)|(?P<import>import\s([^\s]+))|(?P<import_from>from\s([^\s]+)\simport\s(.*)))$')

        for i, line in enumerate(vim.current.buffer[:]):

            cur_line = {
                'n': i
            }

            m = rgx.search(line)

            if m:

                for ltype in [BANG_LINE, WHITE_LINE, IMPORT_LINE, IMPORT_FROM]:

                    if m.group(ltype) is not None:

                        cur_line['type'] = ltype

                        if ltype in [IMPORT_LINE, IMPORT_FROM]:

                            cur_line['type'] = IMPORT_LINE

                            if ltype is IMPORT_FROM:

                                cur_line['module'] = m.group(6)

                                cur_line['sub_modules'] = [x.strip() for x in m.group(7).split(',')]

                                cur_line['import_type'] = IMPORT_FROM

                            else:

                                cur_line['module'] = m .group(4)

                                cur_line['import_type'] = IMPORT_DIRECT

                            with ModuleImporter(cur_line['module']) as module:

                                if module:

                                    cur_line['section'] = module.section

                                else:

                                    cur_line['section'] = ModuleImporter.USER

            else:

                cur_line['type'] = CODE_LINE

            self._lines.append(cur_line)

    def add_import(self, module, submodule=None):

        import_type = IMPORT_DIRECT

        if submodule:

            import_type = IMPORT_FROM

        with ModuleImporter(module) as _module:

            if not _module:

                logger.debug('add_import -> {0!r} is not a module.'.format(module))

                return

            section = _module.section

        logger.debug("New import: {0} {1} => type: {2} section: {3}.".format(
                     module, submodule, import_type, section))

        # Lambda recurses until key_value tuples exhausted, then returns results
        get_lmbda = lambda lines, key_vals: get_lmbda(
            [l for l in lines if l.get(key_vals[0][0]) == key_vals[0][1]],
            key_vals[1:]) if len(key_vals) > 0 else lines

        get_line = lambda lst: lst[0] if lst else False

        line = get_line([l for l in self._lines if l.get('import_type') is import_type
                         and l.get('module') == module])

        if line:

            # This check might be redundant since flake wouldnt trigger on already
            # imported modules
            if import_type is IMPORT_FROM:

                vim.current.buffer[line['n']] = "from {0} import {1}".format(
                    line['module'], ', '.join(line['sub_modules'] + [submodule]))

            return

        elif get_lmbda(self.import_lines, [('module', module)]):
            # import line for this module exists
            line_n = get_lmbda(self.import_lines, [('module', module)])[0]['n'] + 1

        elif get_lmbda(self.import_lines, [('section', section)]):
            # section for this import exists
            line_n = get_lmbda(self.import_lines, [('section', section)])[-1]['n'] + 1

        elif self.import_lines:
            # there are import lines
            if section == 0:

                line_n = self.import_lines[0]['n']

            elif section == 1:

                if get_lmbda(self.import_lines, [('section', 0)]):

                    line_n = get_lmbda(self.import_lines, [('section', 0)])[-1]['n'] + 2

                else:

                    line_n = self.import_lines[0]['n']

            else:

                line_n = self.import_lines[-1]['n'] + 2

        else:
            # first import line in buffer = after first whiteline
            if get_lmbda(self._lines, [('type', WHITE_LINE)]):

                line_n = get_lmbda(self._lines, [('type', WHITE_LINE)])[0]['n'] + 1

            else:

                line_n = 0

        if import_type is IMPORT_DIRECT:

            iline = 'import {0}'.format(module)

        else:

            iline = 'from {0} import {1}'.format(module, submodule)

        self.insert_line(line_n, iline)

        # Add whiteline below new import line
        next_line = self._lines[line_n + 1]
        if (next_line['type'] is not WHITE_LINE or next_line['type'] is IMPORT_LINE and
                next_line.get('section') != section):

            logger.debug('end import section @ {0}.'.format(line_n + 1))

            self.insert_line(line_n + 1, '')

        if sorted([l['n'] for l in self.import_lines] + [line_n])[-1] == line_n:
            # Is last import line, check for second whiteline
            if not self[line_n + 2]['type'] is WHITE_LINE:

                logger.debug("End import sections => line_n: {0}.".format(line_n + 2))

                self.insert_line(line_n + 2, '')

    def insert_line(self, line_n, line):

        logger.debug("INSERT: {0!r} @ {1}.".format(line, line_n))

        cur_pos = vim.current.window.cursor

        cur_buffer = vim.current.buffer[:]

        cur_buffer.insert(line_n, line)

        vim.current.buffer[:] = cur_buffer

        vim.current.window.cursor = (cur_pos[0] + 1, cur_pos[1])

        self._read_buffer()
