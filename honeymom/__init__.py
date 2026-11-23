"""Deprecated alias of the `smartmom` package (SmartMOM was formerly called HoneyMOM).

`import honeymom`, `import honeymom.<module>`, `from honeymom.<module> import ...` and `python -m honeymom ...` keep
working for one release. They resolve to the same module objects as `smartmom`, so there is only one copy of the
application state. Switch scripts, services and imports to `smartmom` / `python -m smartmom`: this alias will be
removed in the next release.
"""
import importlib
import importlib.abc
import importlib.util
import sys
import warnings

import smartmom as _smartmom

warnings.warn('The honeymom package was renamed to smartmom. Use "import smartmom" and "python -m smartmom"; '
              'the honeymom alias will be removed in the next release.', DeprecationWarning, stacklevel=2)

_OLD, _NEW = __name__, 'smartmom'


class _AliasFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Maps honeymom.<x> to the already imported (or newly imported) smartmom.<x> module object."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(_OLD + '.') and fullname != _OLD + '.__main__':
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return importlib.import_module(_NEW + spec.name[len(_OLD):])

    def exec_module(self, module):
        pass


if not any(isinstance(f, _AliasFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _AliasFinder())


def __getattr__(name):
    try:
        return getattr(_smartmom, name)
    except AttributeError:
        try:
            return importlib.import_module(f'{_NEW}.{name}')
        except ModuleNotFoundError:
            raise AttributeError(f'module {_OLD!r} has no attribute {name!r}') from None


def __dir__():
    return sorted(set(globals()) | set(dir(_smartmom)))
