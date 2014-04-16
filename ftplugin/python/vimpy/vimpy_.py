# -*- coding: utf-8 -*-
# dydrmntion@gmail.com ~ 2013

import logging
import re
from StringIO import StringIO

import vim
from pyflakes import reporter, api

from vimpy import buffer_, util

logger = logging.getLogger(__name__)


def do_vimpy(line_n):

    vb = buffer_.VimBuffer()

    line = vb[line_n - 1]

    flake_errors = _flake_line(line_n)

    vimpy_prompt_resolve = bool(int(vim.eval('g:vimpy_prompt_resolve')))

    vimpy_remove_unused = bool(int(vim.eval('g:vimpy_remove_unused')))

    if not flake_errors:

        return

    for mod in flake_errors['undefined']:

        try:

            context = re.search(r'[^\s]*{0}[^\s]*'.format(mod), vim.current.buffer[line['n']]).group()

        except AttributeError:
            # No context found
            context = mod

        if context.rfind('.') != -1 and _is_module(mod):
            # of type: os.path.isdir / re.search, eg. more than 1 word
            vb.add_import(mod)

            continue

        relative_import = _resolve_relative(mod, [l['module'] for l in vb.import_lines])

        if not relative_import and vimpy_prompt_resolve:

            relative_import = ask_module(mod)

        if relative_import:

            vb.add_import(**relative_import)

    if vimpy_remove_unused:

        for mod in flake_errors['unused']:

            vb.remove_import(mod)


def _flake_line(line_n):

    undefined = 'undefined'

    unused = 'unused'
    redefinition = 'redefinition'

    warnings = StringIO()

    errors = StringIO()

    rep = reporter.Reporter(warnings, errors)

    code = '\n'.join(vim.current.buffer[:])

    if api.check(code, 'f', rep):

        warnings.seek(0)

        errors = {
            undefined: [],
            unused: []
        }

        for line, error in [(int(x.split(':')[1]), x) for x in warnings.readlines()]:

            if undefined in error and line == line_n:

                module = error.split()[-1].strip("\n|'")

                errors[undefined].append(module)

            elif unused in error and redefinition not in error:

                module = error.split()[1].strip(" |'")

                errors[unused].append(module)

        return errors


def _is_module(pos_import):

    with util.ModuleImporter(pos_import) as module:

        return module


def _resolve_relative(pos_import, pos_modules):
    # First check already imported modules for pos_import
    candidates = {}
    for _module in pos_modules:

        with util.ModuleImporter(_module) as module:

            try:

                if pos_import in module.sub_modules:

                    candidates[module.module_name] = module.sub_modules[pos_import]

                elif pos_import in module.recursive_sub_modules:

                    candidates[module.module_name] = module.recursive_sub_modules[pos_import]

            except AttributeError:
                # cur module is user module not in pythonpath, skip.
                pass

    if candidates:

        logger.debug(candidates)

        module, mapping = sorted(candidates.items(), key=lambda k: len(k[1]))[0]

        logger.debug(mapping)

        if mapping[0] == module:

            module = '.'.join(mapping)

        return {
            'module': module,
            'submodule': pos_import
        }


def ask_module(rel_import):

    vim.command('let l:module = input("Auto resolve for relative import: {0!r} failed. '
                'Please enter module name: ")'.format(rel_import))

    module_name = vim.eval('l:module').strip()

    if module_name:

        return _resolve_relative(rel_import, [module_name])
