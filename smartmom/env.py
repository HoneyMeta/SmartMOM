"""Environment variables, with the older names still honoured.

New names use the MOM_ prefix (MOM_API_KEY for the stdio MCP key). The older names (HM_*, MES_*, HONEYMOM_API_KEY,
HONEYMES_API_KEY) keep working so existing installs, services and scripts need no change. When both are set, the new
name wins. Defaults (data directory <root>/data, SQLite file mes.db) are unchanged.
"""
import os

LEGACY = {
    'MOM_DATA': 'HM_DATA',
    'MOM_DB': 'MES_DB',
    'MOM_DB_POOL': 'MES_DB_POOL',
    'MOM_SQLITE_TIMEOUT': 'MES_SQLITE_TIMEOUT',
    'MOM_BLANK': 'MES_BLANK',
    'MOM_BACKUP_DIR': 'MES_BACKUP_DIR',
    'MOM_PG_BIN': 'MES_PG_BIN',
    'MOM_PG_ADMIN_URL': 'MES_PG_ADMIN_URL',
    'MOM_TS_TIMESCALE': 'MES_TS_TIMESCALE',
    'MOM_PACKS': 'HM_PACKS',
    'MOM_AI_FIXTURES': 'HM_AI_FIXTURES',
    'MOM_PDF_BROWSER': 'HM_PDF_BROWSER',
    'MOM_LLM_BASE_URL': 'MES_LLM_BASE_URL',
    'MOM_LLM_API_KEY': 'MES_LLM_API_KEY',
    'MOM_LLM_MODEL': 'MES_LLM_MODEL',
    'MOM_API_KEY': ('HONEYMOM_API_KEY', 'HONEYMES_API_KEY'),
}


def get(name: str, default=None):
    """Value of `name`, else of its legacy name(s) (LEGACY), else `default`. Empty strings count as unset."""
    old = LEGACY.get(name) or ()
    for n in (name, *((old,) if isinstance(old, str) else old)):
        v = os.environ.get(n)
        if v not in (None, ''):
            return v
    return default
