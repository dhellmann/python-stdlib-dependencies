#!/usr/bin/env python3

import ast
import collections
import importlib
import os.path
import sys


class Scanner:

    def __init__(self):
        self._imports = collections.defaultdict(list)
        self._errors = {}
        self._seen = set()

    def _get_imports(self, filename):
        if filename in self._seen:
            return
        self._seen.add(filename)
        if filename.endswith('.so'):
            return

        with open(filename, 'r') as f:
            source = f.read()

        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                yield node

    def _get_module_name_from_import(self, import_node):
        #print(ast.dump(import_node))
        if isinstance(import_node, ast.Import):
            return import_node.names[0].name
        return import_node.module

    def scan_module(self, mod):
        filename = getattr(mod, '__file__', None)

        if filename is None:
            # C or builtin module
            return

        for import_node in self._get_imports(mod.__file__):
            self._imports[mod.__name__].append(import_node)
            submod_name = self._get_module_name_from_import(import_node)
            if submod_name in sys.modules:
                submod = sys.modules[submod_name]
            else:
                try:
                    submod = importlib.import_module(submod_name)
                except Exception as err:
                    # Save the error in case we want to report it later.
                    self._errors[mod.__name__] = str(err)
                    continue
            self.scan_module(submod)

    def show_module(self, name, depth=0, shown=None):
        print('{}{}'.format('  ' * depth, name))

        # Avoid recursing after we have shown the dependencies of a
        # module once.
        if shown is None:
            shown = set()
        if name in shown:
            return
        shown.add(name)

        # Show the dependencies.
        for imported in self._imports[name]:
            imported_name = self._get_module_name_from_import(imported)
            self.show_module(imported_name, depth+1, shown)


if __name__ == '__main__':
    import urllib.request
    scanner = Scanner()
    scanner.scan_module(urllib.request)
    scanner.show_module('urllib.request')
