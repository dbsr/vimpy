# -*- coding: utf-8 -*-
# dydrmntion@gmail.com ~ 2013

import os
import imp
import re
import sys
import types
import importlib

from distutils import sysconfig


class ModuleImporter:

    STDLIB = 0

    SITE = 1

    USER = 2

    def __init__(self, module_name):

        self._module_name = module_name

        self.module_name = module_name.split('.')[0]

        self._sub_modules = {}

    def __enter__(self):

        try:

            self.module = importlib.import_module(self.module_name)

        except (ImportError, AttributeError, ValueError):

            pass

        else:

            return self

    def _iter_children(self, m, mpath=[]):

        if not mpath:
            mpath.append(m.__name__)

        for m, mname in [(getattr(m, x), x) for x in dir(m) if x not in self._sub_modules.keys()]:
            self._sub_modules[mname] = mpath

            if isinstance(m, types.ModuleType):
                self._iter_children(m, mpath + [mname])

    @property
    def section(self):

        stdlib_path = [sysconfig.get_python_lib('stdlib')]

        site_path = sysconfig.get_python_lib('purelib')

        # some stdlib modules have different paths inside a virtualenv
        if hasattr(sys, 'real_prefix'):
            import site

            stdlib_path.extend([p for p in site._init_pathinfo() if
                                re.match(sys.real_prefix, p)])

        try:

            fpath = self.module.__file__

        except AttributeError:
            # builtin, thus stdlib
            section = ModuleImporter.STDLIB

        else:

            if re.match(site_path, fpath):

                section = ModuleImporter.SITE

            elif [p for p in stdlib_path if re.match(p, fpath)]:

                section = ModuleImporter.STDLIB

            else:

                section = ModuleImporter.USER

        return section

    @property
    def sub_modules(self):

        if self.module:

            self._iter_children(self.module)

        return self._sub_modules

    @property
    def recursive_sub_modules(self):
        '''If a check whether a submodule exists for this module fails this
        property gets checked. It's a separate property because it is slow(er)
        and unnecesarry most of the time.'''

        # Stolen from the IPython project (http://www.ipython.org).

        try:

            mpath = os.path.dirname(self.module.__file__)

        except AttributeError:

            pass

        else:

            import_re = re.compile(r'(?P<name>[a-zA-Z_][a-zA-Z0-9_]*?)'
                                   r'(?P<package>[/\\]__init__)?'
                                   r'(?P<suffix>%s)$' %
                                   r'|'.join(re.escape(s[0]) for s in imp.get_suffixes()))

            if os.path.isdir(mpath):

                files = []

                for root, dirs, nondirs in os.walk(mpath):

                    subdir = root[len(mpath)+1:]

                    if subdir:
                        files.extend(os.path.join(subdir, f) for f in nondirs)
                        dirs[:] = []

                    else:
                        files.extend(nondirs)

                for f in files:

                    m = import_re.match(f)

                    if m:

                        try:
                            _sm = __import__(self.module_name, fromlist=[m.group('name')])

                        except:

                            pass

                        else:
                            self._iter_children(_sm)

            return self._sub_modules

    def __exit__(self, *args, **kwargs):
        pass
