"""Rename check (1.0.0: HoneyMOM -> SmartMOM): the deprecated `honeymom` alias package and the old env var names.

    python tests/compat_check.py

- `import honeymom` warns (DeprecationWarning) and `honeymom.<module>` is the same module object as `smartmom.<module>`
- `python -m honeymom ...` runs the smartmom command line (with a note on stderr); `python -m smartmom ...` works
- MOM_API_KEY falls back to HONEYMOM_API_KEY, then HONEYMES_API_KEY; the new name wins
"""
import os
import subprocess
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
results = []


def ok(name, cond, detail=''):
    results.append(bool(cond))
    print(('PASS ' if cond else 'FAIL ') + name + (f'  ({detail})' if detail != '' else ''), flush=True)


with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    import honeymom
ok('import honeymom warns with DeprecationWarning', any(issubclass(w.category, DeprecationWarning) for w in caught))

import smartmom  # noqa: E402
import smartmom.db  # noqa: E402
import honeymom.db  # noqa: E402
ok('honeymom.db is smartmom.db (one module object)', honeymom.db is smartmom.db)
from honeymom.services import ai as ai_old  # noqa: E402
from smartmom.services import ai as ai_new  # noqa: E402
ok('from honeymom.services import ai -> smartmom.services.ai', ai_old is ai_new)
from honeymom.migrations import baseline_47 as b_old  # noqa: E402
ok('honeymom.migrations.baseline_47 -> smartmom', b_old is sys.modules['smartmom.migrations.baseline_47'])
ok('attribute access honeymom.seed', honeymom.seed is __import__('smartmom.seed', fromlist=['x']))
ok('no second copy of the package in sys.modules', not any(k.startswith('honeymom.') and v is not sys.modules.get('smartmom' + k[8:])
                                                            for k, v in list(sys.modules.items())))

from smartmom import env  # noqa: E402
saved = {k: os.environ.pop(k, None) for k in ('MOM_API_KEY', 'HONEYMOM_API_KEY', 'HONEYMES_API_KEY')}
try:
    os.environ['HONEYMES_API_KEY'] = 'k-mes'
    ok('MOM_API_KEY <- HONEYMES_API_KEY', env.get('MOM_API_KEY') == 'k-mes')
    os.environ['HONEYMOM_API_KEY'] = 'k-mom'
    ok('MOM_API_KEY <- HONEYMOM_API_KEY (before HONEYMES_API_KEY)', env.get('MOM_API_KEY') == 'k-mom')
    os.environ['MOM_API_KEY'] = 'k-new'
    ok('MOM_API_KEY wins', env.get('MOM_API_KEY') == 'k-new')
    ok('single legacy names still work (MOM_DATA <- HM_DATA)', env.LEGACY['MOM_DATA'] == 'HM_DATA')
finally:
    for k, v in saved.items():
        os.environ.pop(k, None)
        if v is not None:
            os.environ[k] = v


def run_module(mod, *args):
    # runpy with the repository first on sys.path, so this works with any interpreter setup (also embedded Pythons
    # that ignore PYTHONPATH and the current directory)
    code = f'import runpy, sys; sys.path.insert(0, {ROOT!r}); sys.argv = [{mod!r}] + {list(args)!r}; runpy.run_module({mod!r}, run_name="__main__", alter_sys=True)'
    return subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)


r = run_module('smartmom', '--help')
ok('python -m smartmom --help', r.returncode == 0 and 'serve' in r.stdout, r.returncode)
r = run_module('honeymom', '--help')
ok('python -m honeymom --help (deprecated alias)', r.returncode == 0 and 'serve' in r.stdout, r.returncode)
ok('python -m honeymom prints the deprecation note', 'python -m smartmom' in r.stderr, r.stderr.strip()[:120])

n = sum(results)
print(f'\n{n}/{len(results)} passed')
sys.exit(0 if n == len(results) else 1)
