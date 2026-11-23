# SmartMOM plant data replayer - SPDX-License-Identifier: AGPL-3.0-or-later
"""Forward mode: relay the demo ports to a live plant simulator instead of playing back a recording.

Used by the Compose profile "factory" (docker compose --profile factory up). The replayer container shares the network
namespace of the mom container, so the demo data sources of SmartMOM (mqtt://127.0.0.1:1883,
opc.tcp://127.0.0.1:4840/vfactory/, Modbus 127.0.0.1:5020) and the demo plant's simulator address
(http://127.0.0.1:8800) reach SimFactory through this relay. SmartMOM itself needs no configuration change, and
switching back to the recording only means starting without the profile.

Plain TCP relay: every accepted connection opens one connection to the same port on the target host.
"""
import asyncio
import logging
import socket

log = logging.getLogger('replayer.forward')


def resolves(host: str) -> bool:
    try:
        socket.getaddrinfo(host, None)
        return True
    except OSError:
        return False


async def _pipe(reader, writer):
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (ConnectionError, OSError, asyncio.IncompleteReadError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def relay(listen_host: str, port: int, target: str, target_port: int):
    async def handle(cr, cw):
        try:
            ur, uw = await asyncio.wait_for(asyncio.open_connection(target, target_port), 10)
        except (OSError, asyncio.TimeoutError) as ex:
            log.warning('port %s: cannot reach %s:%s (%s)', port, target, target_port, ex)
            cw.close()
            return
        await asyncio.gather(_pipe(cr, uw), _pipe(ur, cw))

    srv = await asyncio.start_server(handle, listen_host, port)
    log.info('forwarding %s:%s -> %s:%s', listen_host, port, target, target_port)
    return srv


async def run_forward(a):
    ports = [p for p in (a.mqtt_port, a.opcua_port, a.modbus_port, a.forward_http_port) if p]
    servers = [await relay(a.host, p, a.forward_to, p) for p in ports]
    log.info('forward mode: %s is up, the recording is not played', a.forward_to)
    try:
        await asyncio.gather(*(s.serve_forever() for s in servers))
    finally:
        for s in servers:
            s.close()
