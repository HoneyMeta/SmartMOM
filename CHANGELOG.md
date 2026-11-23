# Changelog

## 1.0.0 (2026-11-23)

The first open-source release. The feature set is described in the [README](README.md).

### Renamed: HoneyMOM is now SmartMOM (智能 MOM)

SmartMOM was formerly called **HoneyMOM** (蜂元智能 MOM). The new name says what the product is: a manufacturing
operations management (MOM) system. Only the product name changes. The copyright holder and licensor are the same:
蜂元科技（郑州）有限责任公司 (HoneyMeta Technology (Zhengzhou) Co., Ltd.), dev@honeymeta.com.

- Repository: https://github.com/HoneyMeta/SmartMOM.
- README (en/zh), docs, NOTICE, COMMERCIAL-LICENSE, CLA, CONTRIBUTING, SECURITY, THIRD-PARTY-NOTICES, issue and pull
  request templates, CI job names.
- UI:
  - English: SmartMOM. Chinese: 智能 MOM, and the full title `SmartMOM 智能 MOM` on the login page and in the mobile
    app manifest.
  - This covers the page title, top bar, login page, status bar, command center, daily report, tour, the AI
    assistant's greeting, both web catalogues, the backend catalogue and the Chinese source strings that name the
    product.
  - The AI assistant, data Q&A and agent-node prompts, the MCP server (`smartmom`, title 智能 MOM / SmartMOM), the
    API docs title, the test label and the webhook test message.
- Python package `smartmom`: `python -m smartmom serve`, `python -m smartmom create-admin`, `python -m smartmom mcp`
  and so on.
  - `honeymom` stays as a **deprecated alias for one release**. `python -m honeymom ...`, `import honeymom` and
    `import honeymom.<module>` keep working and use the same module objects as `smartmom` (one copy of the
    application state). `python -m honeymom` prints a note on stderr. The alias will be removed in the next release.
- Environment variable for the stdio MCP key: `MOM_API_KEY`. The older names `HONEYMOM_API_KEY` and `HONEYMES_API_KEY`
  are still read; when several are set, the new name wins.
- Docker:
  - The image is `ghcr.io/honeymeta/smartmom` (local build `smartmom:local`), and the image variable is
    `SMARTMOM_IMAGE` (was `HONEYMOM_IMAGE`).
  - The Compose project is `smartmom`, and the default PostgreSQL user, password and database in
    `docker-compose.yml` are `smartmom`.
- Webhook `User-Agent`: `SmartMOM-Webhook/5.0`. Agent export files: `"format": "smartmom-agent"` (import does not
  check the format name, so older exports still import).
- The sister product HoneyFactory is now **SimFactory** (智能仿真工厂, https://github.com/HoneyMeta/SimFactory). Texts
  that name it were updated, including the delivery package README in `smartmom/fixtures/delivery/`.

### Kept unchanged for compatibility

These identifiers keep their names on purpose. Existing installations, scripts, clients and integrations need no
change.

| Kept | Why |
|---|---|
| Environment variables `MOM_*`, and the older `HM_*` / `MES_*` names they replaced | existing services and scripts |
| Data directory `data/`, SQLite file `mes.db`, uploads and backup archive names (`mes-<date>-*.zip`) | an upgraded server finds its data and backups |
| Database schema, table names, migration ids, system parameter and setting keys | existing databases need no migration for the rename |
| PostgreSQL advisory-lock names `honeymes.migrate`, `honeymes.audit.seal`, `honeymes.ts.rollup` | an old and a new server process on the same database still exclude each other |
| Browser storage keys `hm_lang` and the other `hm_*` keys; CSS classes and tokens `hm-*`, `--hm-*` | users keep their settings; internal identifiers |
| Webhook headers `X-HM-Event`, `X-HM-Delivery`, `X-HM-Timestamp`, `X-HM-Signature`; API key prefix `hmk_` | receivers verify these; keys already issued keep working |
| Replay recording format id `honeymom-replay/1` | the shipped recordings and recordings users made carry it |
| Delivery package format name `蜂元交付包 点表格式 v1` | the name SimFactory writes into its packages |
| Backend catalogue ids `蜂元 MES`, `蜂元智能 MES`, `蜂元智能 MOM`, the `测试打印` and `Webhook 测试` variants and the old agent-node prompts | existing databases store these texts (label templates, agent definitions, logs); they stay translatable |
| Demo data source endpoints (`mqtt://127.0.0.1:1883`, `opc.tcp://127.0.0.1:4840/vfactory/`, `127.0.0.1:5020`) and the MQTT topics `vfactory/<plant>/...` | SimFactory protocol identifiers |
| Demo password `honey123`, company name 蜂元科技 / HoneyMeta | not product names |

Upgrading an existing installation:

- Bare metal: change `python -m honeymom serve` to `python -m smartmom serve` in services, scheduled tasks and
  scripts, and `-m honeymom mcp` to `-m smartmom mcp` in MCP client configurations. The old commands keep working in
  this release.
- Docker: the volumes of a pre-release Compose run live under the old project name (`honeymom_mom-data`,
  `honeymom_pg-data`), and that database was created with user, password and database `honeymom`. To keep using them,
  run `docker compose -p honeymom ...` with `POSTGRES_USER=honeymom`, `POSTGRES_PASSWORD=<old password>` and
  `POSTGRES_DB=honeymom` in `.env`.

### New: run SmartMOM against the live plant simulator

- `docker compose --profile factory up` adds a `simfactory` container. It runs `ghcr.io/honeymeta/simfactory:latest`
  with `VF_DEMO=1`, so the same demo plant (foundry-housing) runs live, and its web UI is on port 8800
  (`SIMFACTORY_PORT`).
  - The replayer then relays the demo ports (MQTT 1883, OPC UA 4840, Modbus TCP 5020, web 8800) to SimFactory instead
    of playing back the recording. SmartMOM's demo data sources need no change.
  - Requires Docker Compose 2.20 or later.
- `docker/compose.factory-build.yml` builds SimFactory from a sibling checkout (`SIMFACTORY_SRC`, default
  `../SimFactory`) instead of pulling the image.
- Replayer: `python -m replayer --forward-to HOST [--forward-http-port 8800]` relays the ports to HOST when HOST
  resolves, and plays back the recording otherwise.
- Dockerfile: optional build arguments for mirrors (`NODE_IMAGE`, `PYTHON_IMAGE`, `NPM_REGISTRY`, `DEBIAN_MIRROR`,
  `PIP_MIRROR`), the same as SimFactory's.
- `tests/compat_check.py` (in CI) checks the `honeymom` alias and the old environment variable names.
