# Getting started

This guide gets SmartMOM running with the demo plant, shows where things are, and then walks through a production
first start.

## 1. Start the demo

### With Docker

```bash
git clone https://github.com/HoneyMeta/SmartMOM.git
cd SmartMOM
docker compose up
```

This builds the image on the first run and starts three containers:

| Container | What it does |
|---|---|
| `mom` | SmartMOM: API and web UI on http://localhost:8900 |
| `db` | PostgreSQL 17 (data in the `pg-data` volume) |
| `replayer` | Plays back a recorded 24-hour day of the demo foundry over MQTT, OPC UA and Modbus TCP |

### With the live plant simulator (SimFactory)

[SimFactory](https://github.com/HoneyMeta/SimFactory) (智能仿真工厂) is the plant simulator the recording was made
from. It runs the same demo plant (`foundry-housing`) live, so you can change the speed, inject faults or stop machines
and see the effect in SmartMOM.

```bash
docker compose --profile factory up
```

| Container | What it does |
|---|---|
| `simfactory` | SimFactory (`ghcr.io/honeymeta/simfactory:latest`, `VF_DEMO=1`): simulation, web UI on http://localhost:8800 (`admin` / `honey123`) |
| `replayer` | Plays nothing in this mode. It relays MQTT 1883, OPC UA 4840, Modbus TCP 5020 and the web port 8800 from the `mom` container to `simfactory` |

How it fits together: the demo data sources of SmartMOM (`VF` = `mqtt://127.0.0.1:1883`,
`VF-OPC` = `opc.tcp://127.0.0.1:4840/vfactory/`, `VF-MB` = `127.0.0.1:5020`) and the demo plant's simulator address
(`http://127.0.0.1:8800`) point at `127.0.0.1` inside the `mom` container. The replayer shares that network
namespace. With `--forward-to simfactory` in its command it checks at start-up whether the host name `simfactory`
resolves. With the profile active, it relays the ports to that container. Without the profile, it plays back the
recording. SmartMOM's configuration is the same in both cases, and the point table, layout and 3D models come from the
same delivery package. SimFactory publishes the tags under `vfactory/foundry-housing/...` and the MES gateway topics
`vfactory/foundry-housing/_mes/part` and `.../_mes/event`, exactly as recorded.

Settings (in `.env`, see `docker/env.example`):

- `SIMFACTORY_IMAGE`: the image. To build from a SimFactory checkout instead, add
  `-f docker/compose.factory-build.yml` (it builds `SIMFACTORY_SRC`, default `../SimFactory`).
- `SIMFACTORY_PORT`: the host port of the web UI. Default 8800.
- `VF_LANG`: the SimFactory UI language, `en` or `zh-CN`.

Requires Docker Compose 2.20 or later (optional `depends_on`). Data of the simulator is in the `vf-data` volume.

**Another plant, or SimFactory on another machine.** The demo data sources only fit the demo plant on
`127.0.0.1`. For any other SimFactory plant, connect it the way a real plant is connected, from its delivery package
(**Connectivity -> Overview & Import**, card **Import Delivery Package**):

1. Get the package. Either fill in **Or fetch from URL** with `http://<simfactory host>:8800/api/p/<plant>` and a
   SimFactory token in **Token** (required by SimFactory: an API token from SimFactory's **Settings -> API tokens**, or
   the token of a SimFactory login), then **Fetch Package**. Or download the zip in SimFactory (**Delivery package**
   button, `GET /api/p/<plant>/delivery.zip`) and use **Upload Package (zip)**.
2. Check the preview: devices, point table, protocols, layout and one endpoint per protocol. For new data sources the
   endpoints are the addresses written in the package (SimFactory's own address); existing data sources keep their
   current address. Change an endpoint if SimFactory is reachable under another name, e.g. `mqtt://simfactory:1883`.
3. **Confirm Import**, then open **Tag Check**: tags turn green as values arrive.

For the demo plant the delivery package is already imported (`smartmom/fixtures/delivery/foundry-housing.zip`), which
is why the factory profile needs no onboarding step.

### Without Docker

Python 3.12 and Node.js 20+:

```bash
pip install -r requirements.txt -r replayer/requirements.txt
cd web && npm ci && npm run build && cd ..
python -m replayer                       # terminal 1
MOM_DEMO=1 python -m smartmom serve      # terminal 2 (Windows: set MOM_DEMO=1, then python -m smartmom serve)
```

The database is SQLite in `data/mes.db`. The demo data sources point at the replayer's default ports on
`127.0.0.1`, so nothing else needs configuring. SimFactory in demo mode on the same machine uses the same ports and can
take the replayer's place.

## 2. Log in

Open http://localhost:8900. Demo accounts (password `honey123` for all of them):

| Account | Role |
|---|---|
| `admin` | System administrator |
| `manager` | Plant manager |
| `planner` | Production planner |
| `leader` | Shift / team leader |
| `operator` | Operator |
| `qc` | Quality inspector |
| `maint` | Maintenance |
| `wh` | Warehouse |
| `engineer` | Process engineer |

The demo plant is the fictional "Northfield Castings": melting, molding, shot blasting, six machining centres, a
deburring robot, inspection, an automated warehouse and AGVs. The demo language is English (`MOM_DEMO_LANG=en`);
`MOM_DEMO_LANG=zh` seeds a Chinese dataset instead. The UI language can be switched at any time with **EN / 中** in the
top bar.

Within about a minute of starting, the replayer's data fills the cockpit, the plant map, the live monitor and OEE.
The status bar at the bottom shows the data clock, collector status and machines online.

## 3. Find your way around

- **Left menu:** grouped like ISA-95: Production Operations, Quality Operations, Maintenance Operations, Inventory
  Operations, then planning and business (ERP), factory model and connectivity, AI, master data and System. `/` filters
  the menu.
- **Ctrl+K:** global search for pages, document numbers and commands.
- **?** next to a page title: a guided tour of that page. A welcome tour runs on the first login.
- **AI Assistant** on the right edge: off until an administrator enables AI (see [ai.md](ai.md)).
- **Shop-floor display** (`/screen`), **workstation terminal** (`/station`) and **mobile** (`/m`, installable as a PWA)
  are separate entry points for the shop floor.

A short tour through the demo:

1. **Home:** KPIs per operations area, live plant map, alerts and andon.
2. **Production Operations → Work Orders:** release a work order. The demo also releases work orders automatically as
   the recorded plant produces.
3. **Production Operations → Scheduling & Dispatch:** the finite-capacity schedule and its constraint markers.
4. **Maintenance Operations → Live Monitor** and **OEE:** values from the replayer.
5. **Quality Operations → Quality Overview:** inspections, NCRs and defect Pareto.
6. **Factory Model & Connectivity:** data sources, the tag check and the plant model imported from the demo delivery
   package.

## 4. Production first start

A production install starts empty: no accounts, no demo data, no default password.

With Docker:

```bash
cp docker/env.example .env      # set at least POSTGRES_PASSWORD and TZ
docker compose -f docker-compose.yml -f docker/compose.production.yml up -d
```

Without Docker: start without `MOM_DEMO`, e.g. `python -m smartmom serve --db postgresql+psycopg://...`.

Then:

1. **Create the administrator.** Open the web UI; the login page asks for the first administrator account
   (`GET /api/setup/admin` reports `{"needed": true}` until one exists, `POST /api/setup/admin` creates it). Or on the
   command line:

   ```bash
   python -m smartmom create-admin --username admin                    # asks for the password (min. 8 characters)
   docker compose exec mom python -m smartmom create-admin --username admin
   ```

   `MOM_ADMIN_PASSWORD` supplies the password without a prompt. Once an active administrator exists, both ways refuse
   to create another one; further users are created under **System**.
2. **Setup Wizard.** After the first login the wizard runs: industry template, company information, master data
   import, device connection.
3. **Connect equipment.** Import the delivery package of your plant or add data sources by hand; see
   [connecting-equipment.md](connecting-equipment.md).
4. **Users and roles.** Create accounts and adjust roles, permissions and data scopes under **System**.
5. **Backups.** Check the backup schedule and do a restore drill; see [deployment.md](deployment.md#backups).

Do not switch an existing demo database to production mode: the demo data and accounts stay in the database. Start
production on a new database (with Docker, new volumes).

## Next

- [deployment.md](deployment.md): Docker, bare metal, PostgreSQL, backups, upgrades
- [configuration.md](configuration.md): environment variables, command line, settings
- [connecting-equipment.md](connecting-equipment.md): MQTT, OPC UA, Modbus and other collectors, the replayer
- [ai.md](ai.md): model configuration, AI switches, agents, MCP
