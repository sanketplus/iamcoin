import logging


from aiohttp import web

log = logging.getLogger(__name__)
peers = {}

async def handle_peer_msg(ws):

    async for msg in ws:
        if msg.type == web.WSMsgType.text:
            log.info("Got message: {}".format(msg.data))
            # await ws.send_str("Did you just say, {}".format(msg.data))
        elif msg.type == web.WSMsgType.binary:
            await ws.send_bytes(msg.data)
        elif msg.type in [web.WSMsgType.close, web.WSMsgType.error]:
            log.info("WS close or err: closing connection")
            peers.remove(ws)
            ws.close()


async def broadcast(msg):
    for p in peers:
        await peers[p].send_str(msg)