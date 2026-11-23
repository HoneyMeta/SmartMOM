"""Deprecated: `python -m honeymom ...` runs `python -m smartmom ...` (SmartMOM was formerly called HoneyMOM)."""
import sys

import honeymom  # noqa: F401  (installs the honeymom.* -> smartmom.* alias)
from smartmom.__main__ import main

if __name__ == '__main__':
    sys.stderr.write('Note: "python -m honeymom" is deprecated, use "python -m smartmom" (the package was renamed).\n')
    sys.stderr.flush()
    main()
